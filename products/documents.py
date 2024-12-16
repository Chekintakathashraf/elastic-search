from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product, Tags

@registry.register_document
class ProductDocument(Document):
    # Add NestedField to represent ManyToManyField
    tags = fields.NestedField(properties={
        "tag": fields.KeywordField()
    })

    # Handle ForeignKey Field for brand_name
    brand_name = fields.ObjectField(properties={
        "brand_name": fields.KeywordField()
    })

    class Index:
        name = "products"  # Elasticsearch index name
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Product
        related_models = [Tags]  # Ensure related models are updated in Elasticsearch
        fields = [
            "title",
            "description",
            "category",
            "price",
            "brand",
            "sku",
            "thumbnail",
        ]

    def get_instances_from_related(self, related_instance):
        """
        Updates Elasticsearch index when related models (Tags) are updated.
        """
        if isinstance(related_instance, Tags):
            return related_instance.product_set.all()
