# ATV Texnik Vositalar Hisobga Olish Platformasi
![diagram](/Diagram.png)
https://drawdb.vercel.app/editor?shareId=323cc0c8bbed81299ce512ea4219f28f

### Ma’lumotlar Modeli va Tizim Arxitekturasi Tavsifi

Versiya 1.0

---

# 1. Loyihaning umumiy tavsifi

ATV (Axborot-Texnika Vositalari) platformasi davlat tashkilotlarida mavjud texnik vositalarni **markazlashgan holda hisobga olish, monitoring qilish va tahlil qilish** uchun mo‘ljallangan.

Platforma quyidagi vazifalarni bajaradi:

* barcha hududlarda mavjud texnik vositalarni ro‘yxatga olish
* texnik vositalarning holatini monitoring qilish
* texnik xizmat va ta’mirlarni hisobga olish
* texnik vositalar bilan bog‘liq xarajatlarni kuzatish
* texnik vositalar bo‘yicha analitika va hisobotlar tayyorlash
* kelajakdagi texnik vositalarga bo‘lgan ehtiyojni prognoz qilish

Ushbu tizim rahbariyatga **aniq va real ma’lumotlarga asoslangan qaror qabul qilish imkonini beradi**.

---

# 2. Tizimning asosiy maqsadlari

Platforma quyidagi savollarga doim aniq javob berishi kerak:

* Qaysi viloyatda qaysi texnik vositalar mavjud?
* Qaysi texnik vositalar eskirish bosqichiga yetgan?
* Qaysi hududlarda texnik vositalar yetishmayapti?
* Qaysi texnik vositalarga eng ko‘p mablag‘ sarflanmoqda?
* Keyingi 1–3–5 yil ichida qancha texnik vosita kerak bo‘ladi?

Bu ma’lumotlar asosida tashkilot **texnik rejalashtirishni samarali amalga oshirishi mumkin**.

---

# 3. Tizimning asosiy modullari

Tizim bir nechta asosiy modullardan tashkil topgan.

---

# 3.1 Foydalanuvchilarni boshqarish moduli

Bu modul tizim foydalanuvchilarini va ularning huquqlarini boshqaradi.

Tizimda quyidagi foydalanuvchi rollari bo‘lishi mumkin:

* Super administrator
* Respublika darajasidagi analitik
* Viloyat boshqaruvchisi
* Viloyat operatori
* Auditor

Modul quyidagi ma’lumotlarni saqlaydi:

* foydalanuvchi login ma’lumotlari
* rol va huquqlar
* hududiy kirish chegaralari
* foydalanuvchi profili

Xavfsizlik uchun quyidagi imkoniyatlar mavjud:

* login urinishlarini monitoring qilish
* foydalanuvchi sessiyalarini boshqarish
* qurilmalarni aniqlash
* ikki bosqichli autentifikatsiya

---

# 3.2 Tashkiliy tuzilma moduli

Tizim tashkilotning hududiy va xizmat tuzilmasini aks ettiradi.

Tuzilma quyidagi darajalardan iborat bo‘lishi mumkin:

* Respublika
* Viloyat
* Tuman
* Muassasa / Bo‘linma
* Xizmat yo‘nalishi

Xizmat yo‘nalishlariga misollar:

* Jamoat xavfsizligi
* Tergov
* Yo‘l harakati xavfsizligi
* Migratsiya xizmati
* Aloqa va IT
* Maxsus bo‘linmalar

Bu modul texnik vositalarni **hududlar va xizmat yo‘nalishlari kesimida tahlil qilish imkonini beradi**.

---

# 3.3 Texnik vositalar reyestri

Bu modul tizimning **eng asosiy qismi** hisoblanadi.

Har bir texnik vosita uchun quyidagi ma’lumotlar saqlanadi:

* inventar raqami
* model
* ishlab chiqaruvchi
* seriya raqami
* xarid sanasi
* xarid narxi
* joylashgan hudud
* bo‘linma
* xizmat yo‘nalishi
* texnik holati
* xizmat muddati

Texnik vositalar quyidagi turlarga kirishi mumkin:

* kompyuterlar
* serverlar
* radioaloqa qurilmalari
* videokameralar
* kuzatuv tizimlari
* tarmoq uskunalari

---

# 3.4 Texnik vositalar hayot sikli monitoringi

Har bir texnik vosita o‘z hayot sikliga ega.

Tizim texnik vositalarni quyidagi bosqichlarda kuzatadi:

* yangi texnika
* normal foydalanish
* eskirish bosqichi
* tanqidiy holat

Tizim texnik vositalarning eskirish darajasini avtomatik hisoblaydi.

Bu orqali rahbariyat **texnik vositalarni oldindan yangilashni rejalashtirishi mumkin**.

---

# 3.5 Texnik vositalarni ko‘chirish hisobi

Texnik vositalar bir hududdan boshqasiga o‘tkazilishi mumkin.

Har bir o‘tkazish jarayoni tizimda qayd etiladi.

Quyidagi ma’lumotlar saqlanadi:

* qayerdan o‘tkazildi
* qayerga o‘tkazildi
* qaysi bo‘linmalar o‘rtasida
* kim tomonidan amalga oshirildi
* sana

Bu tizimga **har bir texnik vositaning aniq joylashuvini bilish imkonini beradi**.

---

# 3.6 Ta’mirlash va texnik xizmat moduli

Bu modul texnik vositalarning ta’mirlari va texnik xizmatlarini hisobga oladi.

Ta’mir yozuvlari quyidagi ma’lumotlarni o‘z ichiga oladi:

* muammo tavsifi
* ta’mir sanasi
* ta’mirni amalga oshirgan shaxs yoki tashkilot
* ishlatilgan ehtiyot qismlar
* ta’mir xarajati

Bu ma’lumotlar orqali tizim:

* texnik vositalarning ishonchliligini baholaydi
* ta’mir xarajatlarini tahlil qiladi

---

# 3.7 Moliyaviy xarajatlar moduli

Tizim texnik vositalar bilan bog‘liq barcha moliyaviy xarajatlarni kuzatadi.

Masalan:

* yangi texnika xaridi
* ta’mir xarajatlari
* texnik xizmat ko‘rsatish
* boshqa xarajatlar

Bu modul orqali rahbariyat:

* hududlar kesimida xarajatlarni ko‘rishi
* texnik vositalarning umumiy qiymatini baholashi mumkin.

---

# 3.8 Analitika va prognozlash moduli

Tizim mavjud ma’lumotlar asosida kelajakdagi ehtiyojlarni prognoz qiladi.

Prognoz quyidagi omillarga asoslanadi:

* texnik vositalarning yoshi
* nosozlik statistikasi
* hududdagi ish yuklamasi
* xodimlar soni

Natijada tizim quyidagi prognozlarni taqdim etadi:

* 1 yillik ehtiyoj
* 3 yillik reja
* 5 yillik strategik prognoz

---

# 3.9 Bildirishnomalar tizimi

Tizim foydalanuvchilarga muhim voqealar haqida avtomatik xabar beradi.

Masalan:

* texnik vosita eskirish bosqichiga yetganda
* yangi ta’mir yozuvi yaratilganda
* texnik vosita boshqa hududga o‘tkazilganda
* yangi hisobot tayyor bo‘lganda

---

# 3.10 Audit va nazorat moduli

Tizim barcha muhim amallarni audit jurnalida saqlaydi.

Audit log quyidagilarni yozib boradi:

* amalni bajargan foydalanuvchi
* qaysi ma’lumot o‘zgartirilgan
* eski qiymat
* yangi qiymat
* amal bajarilgan vaqt

Bu tizimda **ma’lumotlar shaffofligini ta’minlaydi**.

---

# 4. Asosiy ma’lumotlar obyektlari

Tizim quyidagi asosiy ma’lumot obyektlariga asoslangan:

* Users (foydalanuvchilar)
* Regions (hududlar)
* Departments (bo‘linmalar)
* Services (xizmat yo‘nalishlari)
* Assets (texnik vositalar)
* Repairs (ta’mirlar)
* Expenses (xarajatlar)
* Forecasts (prognozlar)
* Notifications (bildirishnomalar)

Bu obyektlar o‘zaro bog‘lanib **tizimning umumiy ma’lumotlar modelini hosil qiladi**.

---

# 5. Keyingi bosqich

Ushbu hujjat tizimning **ma’lumotlar modelini tushuntirish uchun tayyorlangan dastlabki versiya** hisoblanadi.

Keyingi bosqichlarda quyidagilar amalga oshiriladi:

* texnik talablarni aniqlashtirish
* qo‘shimcha ma’lumot maydonlarini belgilash
* tizim funksiyalarini kengaytirish

---

# 6. Foydalanuvchi rollari va vakolatlari (User Roles Matrix)

Tizimda foydalanuvchilar turli rollarga ega bo‘lishi mumkin. Har bir rol tizimdagi ma’lumotlarga turli darajada kirish huquqiga ega.

Quyida asosiy rollar va ularning vazifalari keltirilgan.

### Super Administrator

Vazifalari:

* tizimni to‘liq boshqarish
* barcha foydalanuvchilarni boshqarish
* barcha hududlar ma’lumotlarini ko‘rish
* tizim sozlamalarini o‘zgartirish

---

### Respublika Analitigi

Vazifalari:

* barcha hududlar bo‘yicha statistik ma’lumotlarni ko‘rish
* analitik hisobotlarni tayyorlash
* texnik vositalar bo‘yicha prognozlarni ko‘rish

Bu foydalanuvchi odatda **faqat analitika bilan ishlaydi**, lekin ma’lumotlarni o‘zgartirmaydi.

---

### Viloyat Boshqaruvchisi

Vazifalari:

* o‘z viloyati bo‘yicha ma’lumotlarni ko‘rish
* texnik vositalar taqsimotini nazorat qilish
* hisobotlarni ko‘rib chiqish

---

### Viloyat Operatori

Vazifalari:

* yangi texnik vositalarni tizimga kiritish
* ta’mir ma’lumotlarini qo‘shish
* texnik vositalarni boshqa bo‘linmalarga o‘tkazish

Bu foydalanuvchi **faqat o‘z hududi doirasida ishlaydi**.

---

### Auditor

Vazifalari:

* tizimdagi o‘zgarishlarni tekshirish
* audit loglarni ko‘rish
* moliyaviy ma’lumotlarni tahlil qilish

Auditor odatda **ma’lumotlarni o‘zgartirmaydi, faqat tekshiradi**.

---

# 7. Ma’lumotlar oqimi (Data Flow)

Tizimdagi ma’lumotlar quyidagi jarayonlar orqali shakllanadi.

---

### 1. Texnik vositani ro‘yxatga olish

Jarayon:

1. Operator yangi texnik vositani tizimga kiritadi
2. Texnik vositaga inventar raqami beriladi
3. Texnik vosita hudud va bo‘linmaga biriktiriladi
4. Texnik vosita monitoring jarayoniga qo‘shiladi

Natijada texnik vosita **markaziy reyestrga kiritiladi**.

---

### 2. Texnik nosozlikni qayd etish

Jarayon:

1. Operator texnik nosozlik haqida yozuv yaratadi
2. Tizim ta’mir yozuvini yaratadi
3. Ta’mir jarayonida ishlatilgan ehtiyot qismlar kiritiladi
4. Ta’mir xarajatlari hisobga olinadi

Bu ma’lumotlar keyinchalik **analitika va xarajat tahlili uchun ishlatiladi**.

---

### 3. Texnik vositani boshqa hududga o‘tkazish

Jarayon:

1. Operator texnik vosita ko‘chirish so‘rovini yaratadi
2. tizim eski va yangi joylashuvni qayd qiladi
3. transfer tarixi saqlanadi

Natijada tizim har doim **texnik vositaning qayerda ekanligini aniq ko‘rsatadi**.

---

### 4. Analitik hisobot yaratish

Jarayon:

1. tizim mavjud ma’lumotlarni tahlil qiladi
2. texnik vositalarning yoshi hisoblanadi
3. nosozliklar statistikasi olinadi
4. prognozlar shakllantiriladi

Natijada rahbariyat uchun **strategik hisobotlar tayyorlanadi**.

---

# 8. Asosiy tizim jarayonlari (Use Cases)

Quyida tizimda eng ko‘p ishlatiladigan jarayonlar keltirilgan.

---

### Use Case 1 — Yangi texnik vosita qo‘shish

Ishtirokchi: Viloyat operatori

Jarayon:

* foydalanuvchi tizimga kiradi
* yangi texnik vosita formasi ochiladi
* texnik ma’lumotlar kiritiladi
* texnik vosita saqlanadi

Natija: texnik vosita tizimga qo‘shiladi.

---

### Use Case 2 — Ta’mir yozuvini yaratish

Ishtirokchi: Operator

Jarayon:

* texnik vosita tanlanadi
* nosozlik tavsifi kiritiladi
* ta’mir sanasi belgilanadi
* ehtiyot qismlar kiritiladi

Natija: ta’mir tarixi yangilanadi.

---

### Use Case 3 — Texnik vosita holatini kuzatish

Ishtirokchi: Analitik yoki boshqaruvchi

Jarayon:

* tizim texnik vositalar ro‘yxatini ko‘rsatadi
* filtr orqali hudud yoki xizmat tanlanadi
* texnik vositalarning holati ko‘riladi

Natija: rahbariyat texnik vositalar holatini nazorat qiladi.

---

### Use Case 4 — Prognoz hisobotini olish

Ishtirokchi: Respublika analitigi

Jarayon:

* tizim analitik modulini ishga tushiradi
* texnik vositalar statistikasi tahlil qilinadi
* kelajak ehtiyojlari hisoblanadi

Natija: 1–3–5 yillik prognoz shakllanadi.

---

# 9. Xavfsizlik va nazorat

Tizimda ma’lumotlar xavfsizligini ta’minlash uchun quyidagi mexanizmlar ishlatiladi:

* role-based access control (RBAC)
* foydalanuvchi sessiyalarini nazorat qilish
* audit log
* ma’lumotlar o‘zgarish tarixini saqlash

Bu mexanizmlar tizimdagi ma’lumotlarning **xavfsizligi va shaffofligini ta’minlaydi**.

---

# 11. Tizim Arxitekturasi (System Architecture)

ATV platformasi zamonaviy **ko‘p qatlamli (multi-layer) arxitektura** asosida ishlab chiqiladi. Bunday arxitektura tizimni kengaytirish, xavfsizlikni ta’minlash va katta hajmdagi ma’lumotlar bilan ishlash imkonini beradi.

Tizim quyidagi asosiy komponentlardan tashkil topadi:

* Foydalanuvchi interfeysi (Frontend)
* Backend server
* Ma’lumotlar bazasi
* Analitika moduli
* Monitoring va log tizimi
* Integratsiya API

Bu komponentlar o‘zaro API orqali bog‘langan holda ishlaydi.

---

# 11.1 Frontend (Foydalanuvchi interfeysi)

Frontend foydalanuvchilar tizim bilan ishlaydigan asosiy qism hisoblanadi.

Frontend orqali foydalanuvchilar quyidagi amallarni bajaradilar:

* texnik vositalarni ro‘yxatga olish
* texnik vositalar ro‘yxatini ko‘rish
* ta’mir yozuvlarini kiritish
* analitik hisobotlarni ko‘rish
* prognoz natijalarini tahlil qilish

Frontend quyidagi qurilmalarda ishlashi mumkin:

* kompyuter
* planshet
* mobil telefon

Frontend odatda zamonaviy web texnologiyalar yordamida ishlab chiqiladi.

Masalan:

* React
* Vue
* yoki boshqa zamonaviy web framework

---

# 11.2 Backend (Server qismi)

Backend tizimning asosiy logikasini bajaradi.

Backend quyidagi vazifalarni bajaradi:

* foydalanuvchi autentifikatsiyasi
* ma’lumotlarni qayta ishlash
* biznes logikani boshqarish
* ma’lumotlarni saqlash va o‘qish
* API orqali frontend bilan aloqa qilish

Backend server REST API yoki GraphQL orqali ishlashi mumkin.

Backend quyidagi texnologiyalar asosida ishlab chiqilishi mumkin:

* FastAPI
* Python
* Docker konteynerlari

Backend server **markaziy data markazda joylashadi**.

---

# 11.3 Ma’lumotlar bazasi (Database)

Tizim barcha ma’lumotlarni markaziy ma’lumotlar bazasida saqlaydi.

Ma’lumotlar bazasida quyidagi ma’lumotlar saqlanadi:

* foydalanuvchilar
* hududlar
* bo‘linmalar
* texnik vositalar
* ta’mir yozuvlari
* moliyaviy xarajatlar
* prognoz ma’lumotlari

Ma’lumotlar bazasi yuqori ishonchlilikka ega bo‘lishi kerak.

Ko‘pincha quyidagi tizimlar ishlatiladi:

* PostgreSQL
* yoki boshqa enterprise darajadagi DBMS

Ma’lumotlar bazasi muntazam ravishda **zaxira nusxa (backup)** qilinadi.

---

# 11.4 Analitika moduli

Analitika moduli tizimdagi ma’lumotlarni tahlil qiladi.

U quyidagi vazifalarni bajaradi:

* texnik vositalar statistikasi
* eskirish darajasi hisoblash
* nosozliklar statistikasi
* xarajatlar tahlili

Analitika moduli rahbariyat uchun **qaror qabul qilishga yordam beradigan ma’lumotlarni taqdim etadi**.

---

# 11.5 Prognozlash moduli

Prognozlash moduli kelajakdagi texnik ehtiyojlarni hisoblash uchun ishlatiladi.

Prognoz quyidagi ma’lumotlarga asoslanadi:

* texnik vositalarning yoshi
* xizmat muddati
* nosozliklar statistikasi
* hududdagi ish yuklamasi

Natijada tizim quyidagi prognozlarni yaratadi:

* 1 yillik ehtiyoj
* 3 yillik reja
* 5 yillik strategik prognoz

---

# 11.6 Monitoring va log tizimi

Tizim ishlash jarayonida barcha muhim hodisalarni qayd qiladi.

Monitoring tizimi quyidagilarni nazorat qiladi:

* server ishlash holati
* tizim yuklanishi
* xatoliklar
* API so‘rovlari

Log tizimi esa quyidagi ma’lumotlarni saqlaydi:

* foydalanuvchi harakatlari
* tizim xatoliklari
* audit yozuvlari

Bu tizimlar platformaning **barqaror ishlashini ta’minlaydi**.

---

# 11.7 Integratsiya imkoniyatlari

ATV platformasi boshqa davlat axborot tizimlari bilan integratsiya qilinishi mumkin.

Integratsiya quyidagi texnologiyalar orqali amalga oshiriladi:

* REST API
* JSON formatidagi ma’lumot almashinuvi

Bu orqali tizim boshqa platformalar bilan ma’lumot almashishi mumkin.

Masalan:

* kadrlar tizimi
* moliyaviy tizim
* davlat statistik tizimlari

---

# 11.8 Tizim joylashuvi (Deployment)

Tizim markaziy server infratuzilmasida joylashtiriladi.

Arxitektura quyidagicha ishlaydi:

Foydalanuvchi → Frontend → Backend API → Database

Bunday arxitektura:

* xavfsiz
* kengaytiriladigan
* katta hajmdagi ma’lumotlar bilan ishlashga mos

bo‘lib hisoblanadi.
