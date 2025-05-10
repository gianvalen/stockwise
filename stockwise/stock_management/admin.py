from django.contrib import admin
from django.contrib import admin
from .models import Inventory, InventoryMaterial, InventoryUpdate, Material, Offer, OfferPurchaseOrder, OfferRequestDetail, Project, ProjectInventory, PurchaseOrder, PurchaseRequest, RequestDetail

admin.site.register(Inventory)
admin.site.register(InventoryMaterial)
admin.site.register(InventoryUpdate)
admin.site.register(Material)
admin.site.register(Offer)
admin.site.register(OfferPurchaseOrder)
admin.site.register(OfferRequestDetail)
admin.site.register(Project)
admin.site.register(ProjectInventory)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseRequest)
admin.site.register(RequestDetail)
