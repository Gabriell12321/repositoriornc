module RNCAnalytics

using HTTP, JSON3, DataFrames, SQLite, Dates, Statistics

const DB_PATH = get(ENV, "IPPEL_DB", joinpath(@__DIR__, "..", "..", "..", "ippel_system.db"))

function fetch_rncs()
    db = SQLite.DB(DB_PATH)
    try
        df = DataFrame(DBInterface.execute(db, "SELECT id, created_at, status, priority, finalized_at FROM rncs"))
        return df
    finally
        SQLite.close(db)
    end
end

function summarize()
    df = fetch_rncs()
    # parse dates
    if :created_at in names(df)
        df.created_at = DateTime.(string.(df.created_at))
        df.month = Date.(Dates.year.(df.created_at), Dates.month.(df.created_at), 1)
    end
    total = nrow(df)
    finalized = sum(coalesce.(df.status .== "Finalizado", false))
    pending = total - finalized
    by_month = combine(groupby(df, :month), nrow => :count)
    return (; total, finalized, pending, by_month)
end

function handle_summary(::HTTP.Stream)
    s = summarize()
    body = JSON3.write(Dict(
        "total" => s.total,
        "finalized" => s.finalized,
        "pending" => s.pending,
        "by_month" => [Dict("month" => string(row.month), "count" => row.count) for row in eachrow(s.by_month)],
    ))
    return HTTP.Response(200, body; headers = Dict("Content-Type" => "application/json"))
end

function handle_health(::HTTP.Stream)
    return HTTP.Response(200, JSON3.write(Dict("success" => true, "service" => "julia-analytics")); headers = Dict("Content-Type" => "application/json"))
end

function start_server()
    router = HTTP.Router()
    HTTP.register!(router, "GET", "/health", handle_health)
    HTTP.register!(router, "GET", "/summary", handle_summary)
    addr = get(ENV, "JULIA_ANALYTICS_ADDR", "127.0.0.1:8082")
    @info "julia analytics starting" addr DB_PATH
    HTTP.serve(router, addr)
end

end # module

if abspath(PROGRAM_FILE) == @__FILE__
    using .RNCAnalytics
    RNCAnalytics.start_server()
end
