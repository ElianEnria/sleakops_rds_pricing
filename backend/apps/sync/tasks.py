from celery import shared_task
from apps.sync.services import sync_rds_pricing_data

@shared_task
def update_rds_pricing_data_task():
    """
    Tarea de Celery que actualiza los datos de precios de AWS RDS.
    """
    message = sync_rds_pricing_data()
    print(message)  
    return message
