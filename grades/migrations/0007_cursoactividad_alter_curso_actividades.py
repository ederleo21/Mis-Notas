import django.db.models.deletion
from django.db import migrations, models

def migrate_m2m_data(apps, schema_editor):
    Curso = apps.get_model('grades', 'Curso')
    CursoActividad = apps.get_model('grades', 'CursoActividad')
    
    # Intentamos leer de la tabla generada por Django automáticamene antes del cambio
    # Nota: Si el usuario ya falló la migración, la tabla actividades_legacy aún no existe pero la original sí.
    # Usaremos SQL crudo para evitar problemas con modelos que no reflejan el estado actual de la DB.
    db_alias = schema_editor.connection.alias
    from django.db import connections
    with connections[db_alias].cursor() as cursor:
        # Verificamos si la tabla de unión original existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grades_curso_actividades'")
        if cursor.fetchone():
            cursor.execute("SELECT curso_id, actividad_id FROM grades_curso_actividades")
            rows = cursor.fetchall()
            for i, (curso_id, actividad_id) in enumerate(rows):
                CursoActividad.objects.using(db_alias).create(
                    curso_id=curso_id,
                    actividad_id=actividad_id,
                    orden=i + 1
                )

class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0006_remove_actividad_tipo_insumo_alter_actividad_options_and_more'),
    ]

    operations = [
        # 1. Crear el modelo intermedio
        migrations.CreateModel(
            name='CursoActividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveIntegerField(default=0)),
                ('actividad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grades.actividad')),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grades.curso')),
            ],
            options={
                'verbose_name': 'Actividad por Curso',
                'verbose_name_plural': 'Actividades por Curso',
                'ordering': ['orden'],
            },
        ),
        # 2. Migrar los datos de la tabla M2M original a la nueva tabla through
        migrations.RunPython(migrate_m2m_data),
        
        # 3. Eliminar el campo M2M original
        migrations.RemoveField(
            model_name='curso',
            name='actividades',
        ),
        
        # 4. Volver a añadir el campo actividades con el through
        migrations.AddField(
            model_name='curso',
            name='actividades',
            field=models.ManyToManyField(blank=True, related_name='cursos', through='grades.CursoActividad', to='grades.actividad'),
        ),
    ]
