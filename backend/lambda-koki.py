import json
import boto3

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

TABLE_NAME = 'ConcertOrders'
# ARN SNS Kamu sudah dipertahankan
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:374315864590:TicketNotification' 

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    
    # 1. Looping untuk mengambil setiap antrean data dari SQS
    for record in event['Records']:
        # SQS membungkus data aslinya di dalam atribut 'body' berformat string
        payload = json.loads(record['body'])
        
        # Mengekstrak data yang dikirim dari Lambda Kasir
        nama = payload.get('nama', 'Anonim')
        email_pembeli = payload.get('email', 'Tidak ada email')
        tipe_tiket = payload.get('tipeTiket', '-')
        total_harga = payload.get('totalHarga', 0)
        metode_bayar = payload.get('metodePembayaran', 'Credit Card (Simulated)')
        
        # Mengambil ID dan Kode Tiket yang SUDAH DIBUAT oleh Lambda Kasir
        order_id = payload.get('orderId', 'ERROR-ID')
        kode_tiket = payload.get('kodeTiket', 'ERROR-KODE')
        
        # 2. Update status antrean menjadi PAID
        payload['statusPembayaran'] = 'PAID'
        
        # 3. Simpan ke DynamoDB
        # Karena variabel 'payload' sudah berisi JSON lengkap, kita bisa langsung memasukkannya
        table.put_item(Item=payload)
        
        # 4. Format angka harga menjadi Rupiah (contoh: 2250000 -> Rp 2.250.000)
        try:
            harga_format = f"Rp {int(total_harga):,.0f}".replace(',', '.')
        except ValueError:
            harga_format = f"Rp {total_harga}"
        
        # 5. Menyusun dan Mengirim Email (SNS)
        pesan_email = (
            f"Halo {nama}!\n\n"
            f"Pembayaran tiket Anda menggunakan {metode_bayar} telah BERHASIL.\n\n"
            f"=== DETAIL TIKET DIGITAL ===\n"
            f"Tipe Tiket  : {tipe_tiket}\n"
            f"Total Harga : {harga_format}\n"
            f"KODE MASUK  : {kode_tiket}\n"
            f"============================\n\n"
            f"Tunjukkan KODE MASUK ini kepada petugas di pintu masuk konser."
        )
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=pesan_email,
            Subject=f"E-Ticket Anda: {kode_tiket}"
        )
        
        print(f"Berhasil memproses ke DynamoDB & SNS untuk tiket: {kode_tiket}")

    # Mengembalikan respon standar ke AWS SQS tanda bahwa tugas selesai
    return {
        'statusCode': 200,
        'body': json.dumps('Proses Antrean SQS Selesai')
    }
