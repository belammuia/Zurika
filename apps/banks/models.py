from django.db import models


class Bank(models.Model):
    short_name = models.CharField(max_length=20, unique=True)
    cbk_code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.short_name


class BankChannelConfiguration(models.Model):
    class AdapterChoice(models.TextChoices):
        KCB_BUNI = "kcb_buni", "KCB Buni API"    

    bank = models.OneToOneField(Bank, on_delete=models.CASCADE, related_name="channel_config")
    adapter_key = models.CharField(
        max_length=30, 
        choices=AdapterChoice.choices, 
        default=AdapterChoice.KCB_BUNI
    )
