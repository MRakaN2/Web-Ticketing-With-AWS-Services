import json
import boto3
import uuid
import string
import random

sqs = boto3.client('sqs')

# GANTI DENGAN URL SQS MILIKMU DARI TAHAP 1
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/374315864590/AntreanTiket'

def lambda_handler(event, context):
    try:
        # Menangkap data dari API Gateway
        body = json.loads(event.get('body', '{}'))

        # Membuat Kode Tiket dan Order ID di awal agar user langsung dapat balasan
        order_id = str(uuid.uuid4())
        kode_tiket = "TKT-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        body['orderId'] = order_id
        body['kodeTiket'] = kode_tiket
        body['statusPembayaran'] = 'PENDING (Antrean)' 

        # Mengirim data ke SQS (Kertas pesanan ditaruh di papan)
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(body)
        )

        # Mengembalikan respon ke Frontend S3 secara instan!
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            },
            'body': json.dumps({
                'kodeTiket': kode_tiket
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }