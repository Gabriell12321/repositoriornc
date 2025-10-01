from flask import Blueprint, request, render_template
from services.db import get_db_connection, return_db_connection
import datetime

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/report/rnc_by_date')
def rnc_by_date():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Validate the dates
    if not start_date or not end_date:
        return "Erro: Data inicial e final são obrigatórias", 400
        
    try:
        # Ensure we include the full end date (until 23:59:59)
        end_date_with_time = f"{end_date} 23:59:59"
        start_date_with_time = f"{start_date} 00:00:00"
        
        # Get database connection
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query to get RNCs created between the dates
        query = """
        SELECT r.id, r.rnc_number, r.title, r.client, r.equipment, 
               r.created_at, r.finalized_at, u.name as user_name, 
               r.price, r.department
        FROM rnc r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.created_at BETWEEN ? AND ?
        ORDER BY r.created_at
        """
        
        cur.execute(query, (start_date_with_time, end_date_with_time))
        rncs = cur.fetchall()
        
        # Format dates for display
        for rnc in rncs:
            if 'created_at' in rnc and rnc['created_at']:
                try:
                    dt = datetime.datetime.strptime(rnc['created_at'], '%Y-%m-%d %H:%M:%S')
                    rnc['created_at'] = dt.strftime('%d/%m/%Y')
                except:
                    pass
                    
            if 'finalized_at' in rnc and rnc['finalized_at']:
                try:
                    dt = datetime.datetime.strptime(rnc['finalized_at'], '%Y-%m-%d %H:%M:%S')
                    rnc['finalized_at'] = dt.strftime('%d/%m/%Y')
                except:
                    pass
                    
            # Format price if present
            if 'price' in rnc and rnc['price']:
                try:
                    price = float(rnc['price'])
                    rnc['price'] = f"R$ {price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                except:
                    pass
        
        return_db_connection(conn)
        
        # Get some summary statistics
        active_count = sum(1 for rnc in rncs if not rnc.get('finalized_at'))
        finalized_count = sum(1 for rnc in rncs if rnc.get('finalized_at'))
        total_count = len(rncs)
        
        # Format dates for display in the template
        display_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        display_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        
        return render_template(
            'report_rnc_by_date.html',
            rncs=rncs,
            start_date=display_start_date,
            end_date=display_end_date,
            active_count=active_count,
            finalized_count=finalized_count,
            total_count=total_count
        )
        
    except Exception as e:
        return f"Erro ao gerar relatório: {str(e)}", 500
