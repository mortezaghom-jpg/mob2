import 'package:flutter/material.dart';

/// صفحه گزارش‌ها: روزانه/هفتگی/ماهانه/بازه تاریخی/طرف حساب/دسته‌بندی و خروجی Excel/PDF/CSV.
/// در MVP فعلی، ساختار UI و فراخوانی /reports/category-summary پیاده شده؛
/// خروجی Excel/PDF/CSV در فاز بعدی با پکیج‌های excel و pdf در سمت بک‌اند اضافه می‌شود
/// (اندپوینت پیشنهادی: GET /reports/export?format=xlsx|pdf|csv).
class ReportsScreen extends StatelessWidget {
  const ReportsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('گزارش‌ها')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('نوع گزارش', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Wrap(spacing: 8, children: const [
            Chip(label: Text('روزانه')),
            Chip(label: Text('هفتگی')),
            Chip(label: Text('ماهانه')),
            Chip(label: Text('بازه تاریخی')),
            Chip(label: Text('طرف حساب')),
            Chip(label: Text('دسته‌بندی')),
          ]),
          const SizedBox(height: 24),
          Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
            OutlinedButton.icon(onPressed: null, icon: const Icon(Icons.table_chart), label: const Text('Excel')),
            OutlinedButton.icon(onPressed: null, icon: const Icon(Icons.picture_as_pdf), label: const Text('PDF')),
            OutlinedButton.icon(onPressed: null, icon: const Icon(Icons.description), label: const Text('CSV')),
          ]),
          const SizedBox(height: 8),
          const Center(
            child: Text('خروجی فایل در فاز بعدی توسعه فعال می‌شود', style: TextStyle(color: Colors.grey, fontSize: 12)),
          ),
        ],
      ),
    );
  }
}
