# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User

class Inventory(models.Model):
    inventory_id = models.CharField(primary_key=True, max_length=5)
    storage_location = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'inventory'

    def __str__(self):
        return f"{self.inventory_id} - {self.storage_location}"


# class InventoryMaterial(models.Model):
#     material = models.OneToOneField('Material', models.DO_NOTHING, primary_key=True)
#     inventory = models.ForeignKey(Inventory, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'inventory_material'

class InventoryMaterial(models.Model):
    im_id = models.CharField(primary_key=True, max_length=5)  # add an auto PK
    material = models.ForeignKey('Material', models.DO_NOTHING)
    inventory = models.ForeignKey('Inventory', models.DO_NOTHING)
    quantity = models.IntegerField(default=0)

    class Meta:
        # managed = False
        db_table = 'inventory_material'
        unique_together = ('material', 'inventory')

    def __str__(self):
        return f"{self.material} in {self.inventory}"


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
    low_stock_threshold = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'material'

    def __str__(self):
        return f"{self.material_name} ({self.unit})"


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

    def __str__(self):
        return f"{self.project} - {self.inventory}"


class PurchaseOrder(models.Model):
    po_id = models.CharField(primary_key=True, max_length=5)
    delivery_date = models.DateTimeField()
    po_status = models.CharField(max_length=255)

    class Meta:
        # managed = False
        db_table = 'purchase_order'


class PurchaseRequest(models.Model):
    pr_id = models.CharField(primary_key=True, max_length=5)
    request_date = models.DateTimeField()
    last_updated = models.DateTimeField(blank=True, null=True)
    STATUS_CHOICES = [
        ('Waiting for Approval', 'Waiting for Approval'),
        ('Not Approved', 'Not Approved'),
        ('Approved', 'Approved'),
    ]
    request_status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    project = models.ForeignKey(Project, models.DO_NOTHING)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        # managed = False
        db_table = 'purchase_request'


class RequestDetail(models.Model):
    request_detail_id = models.CharField(primary_key=True, max_length=5)
    pr = models.ForeignKey(PurchaseRequest, models.DO_NOTHING)
    material = models.ForeignKey(Material, models.DO_NOTHING)
    quantity = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'request_detail'
