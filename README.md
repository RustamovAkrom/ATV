# ATV Texnik Vositalar Hisobga Olish Platformasi

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
