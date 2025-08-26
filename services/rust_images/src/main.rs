use actix_multipart::Multipart;
use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use bytes::BytesMut;
use futures_util::TryStreamExt as _;
use image::{imageops::FilterType, DynamicImage, ImageFormat, GenericImageView};
use serde::Serialize;
use std::io::Cursor;
use tracing::{error, info};

#[derive(Serialize)]
struct ErrorResponse<'a> {
    success: bool,
    message: &'a str,
}

async fn health() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({"success": true, "service": "rust-images"}))
}

async fn sanitize(mut payload: Multipart) -> actix_web::Result<HttpResponse> {
    let mut data = BytesMut::new();

    while let Ok(Some(mut field)) = payload.try_next().await {
        let cd = field.content_disposition();
        let name = cd.get_name().unwrap_or("").to_string();
        if name != "file" { continue; }
        while let Some(chunk) = field.try_next().await? {
            if data.len() + chunk.len() > 6 * 1024 * 1024 { // 6MB guard
                return Ok(HttpResponse::BadRequest().json(ErrorResponse{ success: false, message: "Arquivo muito grande" }));
            }
            data.extend_from_slice(&chunk);
        }
    }

    if data.is_empty() {
        return Ok(HttpResponse::BadRequest().json(ErrorResponse{ success: false, message: "Arquivo ausente" }));
    }

    let reader = Cursor::new(&data);
    let img = match image::load_from_memory(&data) {
        Ok(i) => i,
        Err(e) => {
            error!(?e, "falha ao decodificar imagem");
            return Ok(HttpResponse::BadRequest().json(ErrorResponse{ success: false, message: "Imagem inválida" }));
        }
    };

    let (w, h) = img.dimensions();
    if w as u64 * h as u64 > 30_000_000 { // 30MP cap
        return Ok(HttpResponse::BadRequest().json(ErrorResponse{ success: false, message: "Imagem muito grande" }));
    }

    let resized: DynamicImage = img.resize(256, 256, FilterType::Lanczos3);

    // Prefer WEBP output, fallback to PNG
    let mut out = Vec::new();
    let mut cursor = Cursor::new(&mut out);
    let mut ok_webp = true;
    if let Err(e) = resized.write_to(&mut cursor, ImageFormat::WebP) {
        ok_webp = false;
        error!(?e, "erro ao escrever webp; tentando png");
    }
    if !ok_webp {
        out.clear();
        cursor.set_position(0);
        if let Err(e) = resized.write_to(&mut cursor, ImageFormat::Png) {
            error!(?e, "erro ao escrever png");
            return Ok(HttpResponse::InternalServerError().json(ErrorResponse{ success: false, message: "Falha no processamento" }));
        }
    }

    Ok(HttpResponse::Ok()
        .content_type(if ok_webp { "image/webp" } else { "image/png" })
        .body(out))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter("info")
        .init();

    let addr = std::env::var("RUST_IMAGES_ADDR").unwrap_or_else(|_| "127.0.0.1:8081".to_string());
    info!(%addr, "rust image service starting");

    HttpServer::new(|| {
        App::new()
            .route("/health", web::get().to(health))
            .route("/sanitize", web::post().to(sanitize))
    })
    .bind(addr)?
    .run()
    .await
}
