from django.core.management.base import BaseCommand
from apps.sync.services import sync_rds_pricing_data

class Command(BaseCommand):
    help = "Importa y sincroniza la información de precios de AWS RDS"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando la sincronización de datos...")
        try:
            sync_rds_pricing_data()
            self.stdout.write(self.style.SUCCESS("Sincronización completada exitosamente."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error durante la sincronización: {e}"))
