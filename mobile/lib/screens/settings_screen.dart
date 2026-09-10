import 'package:flutter/material.dart';
import '../services/db_helper.dart';

/// طبق الزام امنیتی پروژه: هیچ کلید API در اپلیکیشن نیست.
/// این صفحه فقط آدرس Backend را می‌گیرد؛ کلید AI همیشه روی سرور (.env) می‌ماند.
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _urlController = TextEditingController();
  bool _pinEnabled = false;
  bool _biometricEnabled = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final url = await DbHelper.instance.getSetting('backend_url');
    setState(() => _urlController.text = url ?? 'http://10.0.2.2:8000');
  }

  Future<void> _save() async {
    await DbHelper.instance.setSetting('backend_url', _urlController.text.trim());
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('تنظیمات ذخیره شد')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('تنظیمات')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('آدرس سرور Backend', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _urlController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              hintText: 'https://your-backend.example.com',
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'توجه: کلید هوش مصنوعی هرگز در این اپلیکیشن ذخیره نمی‌شود؛ فقط روی سرور Backend نگهداری می‌شود.',
            style: TextStyle(fontSize: 12, color: Colors.grey),
          ),
          const SizedBox(height: 16),
          FilledButton(onPressed: _save, child: const Text('ذخیره')),
          const Divider(height: 40),
          const Text('امنیت ورود', style: TextStyle(fontWeight: FontWeight.bold)),
          SwitchListTile(
            title: const Text('قفل با PIN'),
            value: _pinEnabled,
            onChanged: (v) => setState(() => _pinEnabled = v),
          ),
          SwitchListTile(
            title: const Text('ورود با اثر انگشت / Face ID'),
            value: _biometricEnabled,
            onChanged: (v) => setState(() => _biometricEnabled = v),
          ),
          const Divider(height: 40),
          const Text('پشتیبان‌گیری', style: TextStyle(fontWeight: FontWeight.bold)),
          ListTile(
            leading: const Icon(Icons.backup),
            title: const Text('تهیه فایل پشتیبان'),
            onTap: () {},
          ),
          ListTile(
            leading: const Icon(Icons.restore),
            title: const Text('بازیابی از فایل پشتیبان'),
            onTap: () {},
          ),
        ],
      ),
    );
  }
}
