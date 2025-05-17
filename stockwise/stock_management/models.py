from django.db import models
from django.contrib.auth.models import User


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


class Inventory(models.Model):
    inventory_id = models.CharField(primary_key=True, max_length=5)
    storage_location = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'inventory'

    def __str__(self):
        return f"{self.inventory_id} - {self.storage_location}"

class InventoryMaterial(models.Model):
    im_id = models.CharField(max_length=10, primary_key=True)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    initial_quantity = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        is_update = False

        # Only check for previous record if it's not a brand new object
        if self.pk:
            try:
                old = InventoryMaterial.objects.get(pk=self.pk)
                is_update = True
            except InventoryMaterial.DoesNotExist:
                pass

        if is_update:
            delta = self.quantity - old.quantity

            if delta > 0:
                if self.initial_quantity is None:
                    self.initial_quantity = self.quantity
                else:
                    self.initial_quantity += delta
        else:
            # First creation: set initial_quantity to quantity if not explicitly set
            if self.initial_quantity is None:
                self.initial_quantity = self.quantity

        super().save(*args, **kwargs)


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

class Offer(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    offer_id = models.CharField(primary_key=True, max_length=5)
    offer_date = models.DateTimeField()
    unit_price = models.IntegerField()
    quantity_per_price = models.IntegerField()
    total_quantity = models.IntegerField()
    offer_status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Pending')
    offer_status_proj = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Pending')
    offered_by = models.ForeignKey(User, on_delete=models.CASCADE)

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
    STATUS_CHOICES = [
        ('For Delivery', 'For Delivery'),
        ('Completed', 'Completed'),
    ]

    po_id = models.CharField(primary_key=True, max_length=5)
    delivery_date = models.DateTimeField()
    po_status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='For Delivery') 

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
