# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Seed Reports Data for CityLens
Creates sample citizen reports from 126 wards of Hanoi
Uses MongoDB Atlas
"""

import asyncio
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# MongoDB Atlas connection
MONGODB_ATLAS_URI = os.getenv(
    "MONGODB_ATLAS_URI",
    "mongodb+srv://Khoa09102004:citylens2025@citylensdb.lipe0zx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# Hanoi wards (126 phường/xã)
HANOI_WARDS = [
    # Ba Đình
    "Phường Phúc Xá", "Phường Trúc Bạch", "Phường Vĩnh Phúc", "Phường Cống Vị", 
    "Phường Liễu Giai", "Phường Nguyễn Trung Trực", "Phường Quán Thánh", "Phường Ngọc Hà",
    "Phường Điện Biên", "Phường Đội Cấn", "Phường Ngọc Khánh", "Phường Kim Mã",
    "Phường Giảng Võ", "Phường Thành Công",
    # Hoàn Kiếm
    "Phường Phúc Tân", "Phường Đồng Xuân", "Phường Hàng Mã", "Phường Hàng Buồm",
    "Phường Hàng Đào", "Phường Hàng Bồ", "Phường Cửa Đông", "Phường Lý Thái Tổ",
    "Phường Hàng Bạc", "Phường Hàng Gai", "Phường Chương Dương", "Phường Hàng Trống",
    "Phường Cửa Nam", "Phường Hàng Bông", "Phường Tràng Tiền", "Phường Trần Hưng Đạo",
    "Phường Phan Chu Trinh", "Phường Hàng Bài",
    # Đống Đa
    "Phường Văn Miếu", "Phường Quốc Tử Giám", "Phường Hàng Bột", "Phường Láng Hạ",
    "Phường Láng Thượng", "Phường Ô Chợ Dừa", "Phường Văn Chương", "Phường Cát Linh",
    "Phường Quang Trung", "Phường Khương Thượng", "Phường Ngã Tư Sở", "Phường Khâm Thiên",
    "Phường Trung Phụng", "Phường Trung Liệt", "Phường Phương Liên", "Phường Thịnh Quang",
    "Phường Trung Tự", "Phường Kim Liên", "Phường Phương Mai", "Phường Nam Đồng",
    "Phường Thổ Quan",
    # Hai Bà Trưng  
    "Phường Nguyễn Du", "Phường Bạch Đằng", "Phường Phạm Đình Hổ", "Phường Lê Đại Hành",
    "Phường Đồng Nhân", "Phường Phố Huế", "Phường Đống Mác", "Phường Thanh Lương",
    "Phường Bách Khoa", "Phường Thanh Nhàn", "Phường Cầu Dền", "Phường Bạch Mai",
    "Phường Trương Định", "Phường Đồng Tâm", "Phường Vĩnh Tuy", "Phường Minh Khai",
    "Phường Quỳnh Lôi", "Phường Quỳnh Mai",
    # Cầu Giấy
    "Phường Nghĩa Đô", "Phường Nghĩa Tân", "Phường Mai Dịch", "Phường Dịch Vọng",
    "Phường Dịch Vọng Hậu", "Phường Quan Hoa", "Phường Yên Hòa", "Phường Trung Hòa",
    # Tây Hồ
    "Phường Quảng An", "Phường Nhật Tân", "Phường Tứ Liên", "Phường Phú Thượng",
    "Phường Xuân La", "Phường Thụy Khuê", "Phường Bưởi", "Phường Yên Phụ",
    # Thanh Xuân
    "Phường Thanh Xuân Bắc", "Phường Thanh Xuân Nam", "Phường Thanh Xuân Trung",
    "Phường Khương Đình", "Phường Khương Trung", "Phường Khương Mai", "Phường Hạ Đình",
    "Phường Nhân Chính", "Phường Phương Liệt", "Phường Kim Giang",
    # Long Biên
    "Phường Thượng Thanh", "Phường Ngọc Thụy", "Phường Giang Biên", "Phường Đức Giang",
    "Phường Việt Hưng", "Phường Gia Thụy", "Phường Ngọc Lâm", "Phường Phúc Lợi",
    "Phường Bồ Đề", "Phường Sài Đồng", "Phường Long Biên", "Phường Thạch Bàn",
    "Phường Phúc Đồng", "Phường Cự Khối",
    # Hoàng Mai
    "Phường Mai Động", "Phường Hoàng Văn Thụ", "Phường Giáp Bát", "Phường Lĩnh Nam",
    "Phường Thịnh Liệt", "Phường Trần Phú", "Phường Hoàng Liệt", "Phường Yên Sở",
    "Phường Vĩnh Hưng", "Phường Định Công", "Phường Đại Kim", "Phường Tân Mai",
    "Phường Thanh Trì", "Phường Tương Mai",
    # Nam Từ Liêm
    "Phường Cầu Diễn", "Phường Mỹ Đình 1", "Phường Mỹ Đình 2", "Phường Tây Mỗ",
    "Phường Mễ Trì", "Phường Phú Đô", "Phường Đại Mỗ", "Phường Trung Văn",
    "Phường Phương Canh", "Phường Xuân Phương",
    # Bắc Từ Liêm
    "Phường Thượng Cát", "Phường Liên Mạc", "Phường Đông Ngạc", "Phường Đức Thắng",
    "Phường Thụy Phương", "Phường Tây Tựu", "Phường Xuân Đỉnh", "Phường Xuân Tảo",
    "Phường Minh Khai", "Phường Cổ Nhuế 1", "Phường Cổ Nhuế 2", "Phường Phú Diễn",
    "Phường Phúc Diễn",
]

# Report types
REPORT_TYPES = [
    {"value": "infrastructure", "label": "Hạ tầng", "icon": "🏗️"},
    {"value": "environment", "label": "Môi trường", "icon": "🌿"},
    {"value": "security", "label": "An ninh trật tự", "icon": "🔒"},
    {"value": "traffic", "label": "Giao thông", "icon": "🚗"},
    {"value": "sanitation", "label": "Vệ sinh", "icon": "🧹"},
    {"value": "lighting", "label": "Chiếu sáng", "icon": "💡"},
    {"value": "water", "label": "Cấp thoát nước", "icon": "💧"},
    {"value": "other", "label": "Khác", "icon": "📋"},
]

# Sample reports content
SAMPLE_REPORTS = {
    "infrastructure": [
        {
            "title": "Đường hỏng, nhiều ổ gà",
            "content": "Đoạn đường trước cổng trường tiểu học có nhiều ổ gà rất nguy hiểm, đã có nhiều người bị ngã xe. Kính đề nghị cơ quan chức năng sớm khắc phục.",
        },
        {
            "title": "Vỉa hè bị sụt lún",
            "content": "Vỉa hè khu vực chợ bị sụt lún nghiêm trọng do thi công ngầm hóa cáp điện. Gây mất an toàn cho người đi bộ, đặc biệt là người già và trẻ em.",
        },
        {
            "title": "Cầu vượt bộ hành hư hỏng",
            "content": "Lan can cầu vượt bộ hành bị gỉ sét, một số thanh đã bị gãy. Đèn chiếu sáng trên cầu không hoạt động.",
        },
        {
            "title": "Nắp cống mất, gây nguy hiểm",
            "content": "Nắp cống trên vỉa hè bị mất, để lộ miệng cống sâu khoảng 1m. Rất nguy hiểm đặc biệt vào ban đêm.",
        },
    ],
    "environment": [
        {
            "title": "Ô nhiễm không khí do đốt rác",
            "content": "Khu vực bãi đất trống cuối ngõ thường xuyên có người đốt rác thải, khói đen mù mịt ảnh hưởng đến sức khỏe cư dân xung quanh.",
        },
        {
            "title": "Tiếng ồn từ công trình xây dựng",
            "content": "Công trình xây dựng gần khu dân cư thi công cả đêm, tiếng ồn lớn ảnh hưởng giấc ngủ của người dân. Đề nghị quy định giờ thi công.",
        },
        {
            "title": "Cây xanh chết, cần thay thế",
            "content": "Hàng cây bàng trên vỉa hè đã chết khô, cần được thay thế bằng cây mới để tạo bóng mát cho khu vực.",
        },
        {
            "title": "Bụi mịn từ xe tải chở vật liệu",
            "content": "Xe tải chở cát đá từ công trình thường không che bạt, gây bụi mù mịt trên đường. Đề nghị xử lý nghiêm.",
        },
    ],
    "security": [
        {
            "title": "Trộm cắp xe máy xảy ra thường xuyên",
            "content": "Khu vực ngõ nhỏ thường xuyên xảy ra trộm cắp xe máy vào ban đêm. Đề nghị tăng cường tuần tra và lắp camera giám sát.",
        },
        {
            "title": "Thanh niên tụ tập đua xe",
            "content": "Đêm cuối tuần thường có nhóm thanh niên tụ tập đua xe gây mất an ninh trật tự và nguy hiểm cho người đi đường.",
        },
        {
            "title": "Đèn đường không hoạt động",
            "content": "Toàn bộ đèn đường trong ngõ không hoạt động đã hơn 1 tuần, gây mất an ninh và nguy hiểm khi đi lại ban đêm.",
        },
    ],
    "traffic": [
        {
            "title": "Nút giao thông thường xuyên tắc nghẽn",
            "content": "Ngã tư này không có đèn tín hiệu, vào giờ cao điểm thường xuyên xảy ra ùn tắc kéo dài. Đề nghị lắp đèn giao thông.",
        },
        {
            "title": "Biển báo giao thông bị che khuất",
            "content": "Biển báo cấm rẽ trái bị cây xanh che khuất, nhiều người vi phạm do không nhìn thấy biển.",
        },
        {
            "title": "Xe đỗ sai quy định gây cản trở",
            "content": "Nhiều xe ô tô đỗ dưới lòng đường gây cản trở giao thông, đặc biệt là xe taxi và xe công nghệ.",
        },
        {
            "title": "Vạch kẻ đường mờ, khó nhận biết",
            "content": "Vạch sơn phân làn đường đã mờ hết, gây khó khăn cho người tham gia giao thông, đặc biệt vào ban đêm và trời mưa.",
        },
    ],
    "sanitation": [
        {
            "title": "Rác thải chất đống trên vỉa hè",
            "content": "Rác thải tích tụ nhiều ngày không được thu gom, bốc mùi hôi thối và thu hút ruồi muỗi. Ảnh hưởng vệ sinh môi trường.",
        },
        {
            "title": "Cống thoát nước bị tắc",
            "content": "Cống thoát nước bị tắc, mỗi khi mưa nước tràn lên đường gây ngập úng. Đề nghị nạo vét cống.",
        },
        {
            "title": "Nhà vệ sinh công cộng bẩn",
            "content": "Nhà vệ sinh công cộng tại khu vực công viên rất bẩn, không có người dọn dẹp, thiếu nước và giấy vệ sinh.",
        },
    ],
    "lighting": [
        {
            "title": "Đèn đường không sáng",
            "content": "Toàn bộ đèn đường trên đoạn đường dài khoảng 200m không hoạt động, gây mất an toàn khi đi lại ban đêm.",
        },
        {
            "title": "Đèn nhấp nháy liên tục",
            "content": "Đèn đường trước nhà tôi nhấp nháy liên tục suốt đêm, gây khó chịu và ảnh hưởng giấc ngủ.",
        },
        {
            "title": "Cột điện nghiêng, nguy cơ đổ",
            "content": "Cột điện chiếu sáng bị nghiêng khoảng 30 độ sau cơn bão, có nguy cơ đổ gây nguy hiểm.",
        },
    ],
    "water": [
        {
            "title": "Rò rỉ nước đường ống",
            "content": "Đường ống nước sạch bị rò rỉ tại nút giao, nước chảy lãng phí đã nhiều ngày không thấy sửa chữa.",
        },
        {
            "title": "Nước sinh hoạt có mùi lạ",
            "content": "Nước máy sinh hoạt mấy ngày nay có mùi tanh và màu vàng nhạt. Không biết có an toàn để sử dụng không.",
        },
        {
            "title": "Cống thoát nước bị tràn",
            "content": "Mỗi khi mưa to, cống thoát nước bị tràn ngập lên đường và vào nhà dân. Đề nghị nâng cấp hệ thống thoát nước.",
        },
    ],
    "other": [
        {
            "title": "Quảng cáo rao vặt dán bừa bãi",
            "content": "Tờ rơi quảng cáo dán khắp nơi trên tường, cột điện, cây xanh gây mất mỹ quan đô thị.",
        },
        {
            "title": "Chó thả rông không có người trông",
            "content": "Nhiều chó thả rông trên đường không có người trông, gây mất an toàn cho người đi bộ và trẻ em.",
        },
        {
            "title": "Hàng rong lấn chiếm vỉa hè",
            "content": "Nhiều hàng rong bày bán trên vỉa hè gây cản trở người đi bộ, buộc người đi bộ phải đi xuống lòng đường.",
        },
    ],
}

# Sample image URLs (using placeholder images)
SAMPLE_IMAGES = {
    "infrastructure": [
        "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=400&h=300&fit=crop",
    ],
    "environment": [
        "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=400&h=300&fit=crop",
    ],
    "security": [
        "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=400&h=300&fit=crop",
    ],
    "traffic": [
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400&h=300&fit=crop",
    ],
    "sanitation": [
        "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=400&h=300&fit=crop",
    ],
    "lighting": [
        "https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=400&h=300&fit=crop",
    ],
    "water": [
        "https://images.unsplash.com/photo-1584824486509-112e4181ff6b?w=400&h=300&fit=crop",
    ],
    "other": [
        "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=400&h=300&fit=crop",
    ],
}

# Coordinates for Hanoi center
HANOI_CENTER = {"lat": 21.0285, "lng": 105.8542}


def get_random_location():
    """Generate random location within Hanoi area"""
    lat = HANOI_CENTER["lat"] + random.uniform(-0.05, 0.05)
    lng = HANOI_CENTER["lng"] + random.uniform(-0.05, 0.05)
    return {"lat": lat, "lng": lng}


def get_random_date(days_back: int = 30) -> datetime:
    """Generate random date within the last N days"""
    return datetime.utcnow() - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )


def generate_report(report_type: str, ward: str) -> Dict[str, Any]:
    """Generate a single report"""
    report_content = random.choice(SAMPLE_REPORTS[report_type])
    
    # Random status with weighted distribution
    status_weights = [0.3, 0.25, 0.35, 0.1]  # pending, processing, resolved, rejected
    status = random.choices(
        ["pending", "processing", "resolved", "rejected"],
        weights=status_weights
    )[0]
    
    # Generate media (50% chance of having images)
    media = []
    if random.random() > 0.5:
        images = SAMPLE_IMAGES.get(report_type, [])
        if images:
            num_images = random.randint(1, min(3, len(images)))
            for img_url in random.sample(images, num_images):
                media.append({
                    "uri": img_url,
                    "type": "image",
                    "filename": f"report_image_{random.randint(1000, 9999)}.jpg"
                })
    
    created_at = get_random_date(30)
    updated_at = created_at + timedelta(hours=random.randint(0, 48)) if status != "pending" else created_at
    
    # Admin note for processed/resolved reports
    admin_note = None
    if status == "processing":
        admin_note = random.choice([
            "Đã tiếp nhận, đang phối hợp với đơn vị liên quan xử lý.",
            "Đã chuyển đơn vị chức năng xử lý.",
            "Đang khảo sát thực địa.",
        ])
    elif status == "resolved":
        admin_note = random.choice([
            "Đã khắc phục xong. Cảm ơn bạn đã phản ánh.",
            "Vấn đề đã được giải quyết. Xin cảm ơn!",
            "Đã sửa chữa hoàn thành.",
        ])
    elif status == "rejected":
        admin_note = random.choice([
            "Nội dung phản ánh không thuộc thẩm quyền xử lý.",
            "Thông tin không chính xác.",
            "Trùng lặp với phản ánh trước đó.",
        ])
    
    return {
        "_id": ObjectId(),
        "reportType": report_type,
        "ward": ward,
        "addressDetail": random.choice([
            f"Số {random.randint(1, 200)}, ngõ {random.randint(1, 50)}",
            f"Khu vực gần chợ",
            f"Đối diện trường học",
            f"Gần công viên",
            "",
        ]),
        "location": get_random_location(),
        "title": report_content["title"],
        "content": report_content["content"],
        "media": media,
        "userId": f"user_{random.randint(1000, 9999)}" if random.random() > 0.3 else None,
        "status": status,
        "adminNote": admin_note,
        "createdAt": created_at,
        "updatedAt": updated_at,
    }


async def seed_reports(num_reports: int = 50):
    """Seed reports to MongoDB Atlas"""
    print(f"🌱 Seeding {num_reports} reports to MongoDB Atlas...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_ATLAS_URI)
    db = client.citylens
    reports_collection = db.reports
    
    # Clear existing reports (optional)
    existing_count = await reports_collection.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing reports.")
        user_input = input("Do you want to delete existing reports? (y/n): ")
        if user_input.lower() == 'y':
            await reports_collection.delete_many({})
            print("🗑️  Deleted existing reports.")
    
    # Generate reports
    reports = []
    report_types = [rt["value"] for rt in REPORT_TYPES]
    
    for i in range(num_reports):
        report_type = random.choice(report_types)
        ward = random.choice(HANOI_WARDS)
        report = generate_report(report_type, ward)
        reports.append(report)
        
        if (i + 1) % 10 == 0:
            print(f"📝 Generated {i + 1}/{num_reports} reports...")
    
    # Insert to MongoDB
    result = await reports_collection.insert_many(reports)
    print(f"✅ Successfully inserted {len(result.inserted_ids)} reports!")
    
    # Print summary
    print("\n📊 Summary:")
    for rt in report_types:
        count = len([r for r in reports if r["reportType"] == rt])
        print(f"   {rt}: {count}")
    
    print(f"\n📍 Locations covered: {len(set(r['ward'] for r in reports))} wards")
    
    # Status summary
    print("\n📈 Status distribution:")
    for status in ["pending", "processing", "resolved", "rejected"]:
        count = len([r for r in reports if r["status"] == status])
        print(f"   {status}: {count}")
    
    # Close connection
    client.close()
    print("\n🎉 Done!")


async def add_sample_comments(num_comments: int = 30):
    """Add sample comments to existing reports"""
    print(f"💬 Adding {num_comments} sample comments...")
    
    client = AsyncIOMotorClient(MONGODB_ATLAS_URI)
    db = client.citylens
    reports_collection = db.reports
    comments_collection = db.comments
    
    # Get random reports
    reports = await reports_collection.find({}).to_list(length=100)
    if not reports:
        print("❌ No reports found. Please seed reports first.")
        client.close()
        return
    
    sample_comments = [
        "Tôi cũng gặp vấn đề tương tự ở khu vực gần đó.",
        "Mong cơ quan chức năng sớm xử lý!",
        "Đã phản ánh nhiều lần nhưng chưa được giải quyết.",
        "Cảm ơn bạn đã báo cáo vấn đề này.",
        "Tình trạng này đã kéo dài hơn 1 tháng.",
        "Rất bức xúc vì ảnh hưởng đến sinh hoạt hàng ngày.",
        "Mong được xử lý sớm, tình hình ngày càng nghiêm trọng.",
        "Đồng ý với phản ánh này, cần có biện pháp ngay.",
    ]
    
    admin_comments = [
        "Đã tiếp nhận phản ánh. Xin cảm ơn!",
        "Chúng tôi đang phối hợp với đơn vị liên quan để xử lý.",
        "Vấn đề đã được chuyển đến phòng ban chuyên môn.",
        "Dự kiến khắc phục trong 3-5 ngày làm việc.",
    ]
    
    comments = []
    for _ in range(num_comments):
        report = random.choice(reports)
        is_admin = random.random() < 0.3  # 30% admin comments
        
        comment = {
            "_id": ObjectId(),
            "reportId": str(report["_id"]),
            "userId": "admin" if is_admin else f"user_{random.randint(1000, 9999)}",
            "userName": "Quản trị viên" if is_admin else f"Người dân {random.randint(1, 100)}",
            "content": random.choice(admin_comments if is_admin else sample_comments),
            "createdAt": get_random_date(7),
            "updatedAt": datetime.utcnow(),
        }
        comments.append(comment)
    
    result = await comments_collection.insert_many(comments)
    print(f"✅ Added {len(result.inserted_ids)} comments!")
    
    client.close()


if __name__ == "__main__":
    print("=" * 50)
    print("🏙️  CityLens Reports Seeder")
    print("=" * 50)
    print("\nOptions:")
    print("1. Seed reports only (50 reports)")
    print("2. Seed reports and comments")
    print("3. Add comments to existing reports")
    print("4. Custom number of reports")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == "1":
        asyncio.run(seed_reports(50))
    elif choice == "2":
        asyncio.run(seed_reports(50))
        asyncio.run(add_sample_comments(30))
    elif choice == "3":
        asyncio.run(add_sample_comments(30))
    elif choice == "4":
        num = int(input("Enter number of reports to seed: "))
        asyncio.run(seed_reports(num))
    else:
        print("Invalid choice.")
