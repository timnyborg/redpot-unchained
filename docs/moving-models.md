When a feature grows to a certain size, you may want to give it its own dedicated app, and move the relevant models to it.

If you move the model from one app's `models.py` to the other's, and run `python manage.py makemigrations`, Django will create migrations that drop and then recreate the table, which isn't ideal.  Running the migrations on a test database will result in an error because they try to recreate a table that already exists.

To fix this, all we need to do is the generated migration actions in `migrations.SeparateDatabaseAndState`, so the migration updates the application's state without touching the database.


For example, a migration moving three models from the `fee` app to `bookings` will produce the following migration in the `fee` app:
```python
# fees/models.py
class Migration(migrations.Migration):
    ...
    operations = [
        migrations.DeleteModel(
            name='Accommodation',
        ),
        migrations.DeleteModel(
            name='Catering',
        ),
        migrations.DeleteModel(
            name='Limit',
        )
    ]
```

We just move the operations into the `state_operations` argument of `SeparateDatabaseAndState`, while leaving `database_operations` empty:

```python
# fees/models.py
class Migration(migrations.Migration):
    ...
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='Accommodation',
                ),
                migrations.DeleteModel(
                    name='Catering',
                ),
                migrations.DeleteModel(
                    name='Limit',
                )
            ],
            database_operations=[]
        ),
    ]
```

We need to do the same to the `CreateModel` operations in the new app, as well as any `ForeignKey`-related operations that may have been created at the same time (`RemoveField`, `AlterField`).  With both sides done, the migrations should work just fine.

Since we set `db_table` for our models, the table name is preserved without any additional effort.

For a detailed example, see [realpython](https://realpython.com/move-django-model/#the-django-way-rename-the-table)
