# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


# class AuthGroup(models.Model):
#     name = models.CharField(unique=True, max_length=150)

#     class Meta:
#         managed = False
#         db_table = 'auth_group'


# class AuthGroupPermissions(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
#     permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'auth_group_permissions'
#         unique_together = (('group', 'permission'),)


# class AuthPermission(models.Model):
#     name = models.CharField(max_length=255)
#     content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
#     codename = models.CharField(max_length=100)

#     class Meta:
#         managed = False
#         db_table = 'auth_permission'
#         unique_together = (('content_type', 'codename'),)


# class AuthUser(models.Model):
#     password = models.CharField(max_length=128)
#     last_login = models.DateTimeField(blank=True, null=True)
#     is_superuser = models.BooleanField()
#     username = models.CharField(unique=True, max_length=150)
#     first_name = models.CharField(max_length=150)
#     last_name = models.CharField(max_length=150)
#     email = models.CharField(max_length=254)
#     is_staff = models.BooleanField()
#     is_active = models.BooleanField()
#     date_joined = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'auth_user'


# class AuthUserGroups(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     user = models.ForeignKey(AuthUser, models.DO_NOTHING)
#     group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'auth_user_groups'
#         unique_together = (('user', 'group'),)


# class AuthUserUserPermissions(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     user = models.ForeignKey(AuthUser, models.DO_NOTHING)
#     permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'auth_user_user_permissions'
#         unique_together = (('user', 'permission'),)


# class DjangoAdminLog(models.Model):
#     action_time = models.DateTimeField()
#     object_id = models.TextField(blank=True, null=True)
#     object_repr = models.CharField(max_length=200)
#     action_flag = models.SmallIntegerField()
#     change_message = models.TextField()
#     content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
#     user = models.ForeignKey(AuthUser, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'django_admin_log'


# class DjangoContentType(models.Model):
#     app_label = models.CharField(max_length=100)
#     model = models.CharField(max_length=100)

#     class Meta:
#         managed = False
#         db_table = 'django_content_type'
#         unique_together = (('app_label', 'model'),)


# class DjangoMigrations(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     app = models.CharField(max_length=255)
#     name = models.CharField(max_length=255)
#     applied = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'django_migrations'


# class DjangoSession(models.Model):
#     session_key = models.CharField(primary_key=True, max_length=40)
#     session_data = models.TextField()
#     expire_date = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'django_session'


class Inventory(models.Model):
    inventory_id = models.CharField(primary_key=True, max_length=5)
    storage_location = models.CharField(max_length=255)

    class Meta:
        # managed = False
        db_table = 'inventory'


class InventoryMaterial(models.Model):
    material = models.OneToOneField('Material', models.DO_NOTHING, primary_key=True)
    inventory = models.ForeignKey(Inventory, models.DO_NOTHING)

    class Meta:
        # managed = False
        db_table = 'inventory_material'


class InventoryUpdate(models.Model):
    inventory_update_id = models.CharField(primary_key=True, max_length=5)
    po = models.ForeignKey('PurchaseOrder', models.DO_NOTHING)
    inventory = models.ForeignKey(Inventory, models.DO_NOTHING)
    date_updated = models.DateTimeField()

    class Meta:
        # managed = False
        db_table = 'inventory_update'


class Material(models.Model):
    material_id = models.CharField(primary_key=True, max_length=5)
    material_name = models.CharField(max_length=255)
    material_type = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    current_amount = models.IntegerField()
    low_stock_threshold = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'material'

    def __str__(self):
        return f"{self.material_name}"


class Offer(models.Model):
    offer_id = models.CharField(primary_key=True, max_length=5)
    offer_date = models.DateTimeField()
    unit_price = models.IntegerField()
    quantity_per_price = models.IntegerField()
    total_quantity = models.IntegerField()
    offer_status = models.CharField(max_length=255)

    class Meta:
        # managed = False
        db_table = 'offer'


class OfferPurchaseOrder(models.Model):
    po = models.OneToOneField('PurchaseOrder', models.DO_NOTHING, primary_key=True)
    offer = models.ForeignKey(Offer, models.DO_NOTHING)

    class Meta:
        # managed = False
        db_table = 'offer_purchase_order'


class OfferRequestDetail(models.Model):
    offer = models.OneToOneField(Offer, models.DO_NOTHING, primary_key=True)
    request_detail = models.ForeignKey('RequestDetail', models.DO_NOTHING)

    class Meta:
        # managed = False
        db_table = 'offer_request_detail'


class Project(models.Model):
    project_id = models.CharField(primary_key=True, max_length=5)
    project_name = models.CharField(max_length=255)
    project_location = models.CharField(max_length=255)

    class Meta:
        # managed = False
        db_table = 'project'

    def __str__(self):
        return f"{self.project_name}"


class ProjectInventory(models.Model):
    project = models.OneToOneField(Project, models.DO_NOTHING, primary_key=True)
    inventory = models.ForeignKey(Inventory, models.DO_NOTHING)

    class Meta:
        # managed = False
        db_table = 'project_inventory'


class PurchaseOrder(models.Model):
    po_id = models.CharField(primary_key=True, max_length=5)
    delivery_date = models.DateTimeField()
    po_status = models.CharField(max_length=255)

    class Meta:
        # managed = False
        db_table = 'purchase_order'

    def __str__(self):
        return f"{self.po_id} - {self.po_status}"


class PurchaseRequest(models.Model):
    pr_id = models.CharField(primary_key=True, max_length=5)
    request_date = models.DateTimeField()
    last_updated = models.DateTimeField(blank=True, null=True)
    request_status = models.CharField(max_length=255)

    class Meta:
        # managed = False
        db_table = 'purchase_request'

    def __str__(self):
        return f"{self.pr_id} - {self.request_status}"


class RequestDetail(models.Model):
    request_detail_id = models.CharField(primary_key=True, max_length=5)
    pr = models.ForeignKey(PurchaseRequest, models.DO_NOTHING)
    material = models.ForeignKey(Material, models.DO_NOTHING)
    quantity = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'request_detail'

    def __str__(self):
        return f"{self.material} - {self.quantity}"
