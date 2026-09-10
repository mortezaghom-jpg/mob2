import 'package:flutter/material.dart';

class CategoriesScreen extends StatefulWidget {
  const CategoriesScreen({super.key});
  @override
  State<CategoriesScreen> createState() => _CategoriesScreenState();
}

class _CategoriesScreenState extends State<CategoriesScreen> {
  // دسته‌بندی‌های پیش‌فرض سیستم (همان چیزی که در schema.sql هم درج می‌شود)
  final List<String> _categories = [
    'تدارکات', 'خرید کالا', 'حمل و نقل', 'کرایه', 'تعمیرات',
    'ابزار و تجهیزات', 'لوازم مصرفی', 'ایمنی', 'برق', 'مکانیک',
    'اداری', 'پذیرایی', 'سایر',
  ];

  void _addCategory() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('دسته‌بندی جدید'),
        content: TextField(controller: controller, decoration: const InputDecoration(hintText: 'نام دسته‌بندی')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('انصراف')),
          FilledButton(
            onPressed: () {
              if (controller.text.trim().isNotEmpty) {
                setState(() => _categories.add(controller.text.trim()));
                // TODO: هم‌زمان با POST به یک اندپوینت /categories روی بک‌اند ثبت شود
              }
              Navigator.pop(ctx);
            },
            child: const Text('افزودن'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('دسته‌بندی‌ها')),
      body: ListView.builder(
        itemCount: _categories.length,
        itemBuilder: (context, i) => ListTile(
          leading: const Icon(Icons.label_outline),
          title: Text(_categories[i]),
        ),
      ),
      floatingActionButton: FloatingActionButton(onPressed: _addCategory, child: const Icon(Icons.add)),
    );
  }
}
