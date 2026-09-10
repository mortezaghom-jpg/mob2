import 'package:flutter/material.dart';
import '../services/api_service.dart';

/// ثبت دستی: کاربر می‌تواند به‌جای صحبت کردن، همان جمله را تایپ کند.
/// از همان مسیر AI عبور می‌کند (متن -> AI -> تایید -> ثبت) تا منطق یکسان بماند.
class ManualEntryScreen extends StatefulWidget {
  const ManualEntryScreen({super.key});
  @override
  State<ManualEntryScreen> createState() => _ManualEntryScreenState();
}

class _ManualEntryScreenState extends State<ManualEntryScreen> {
  final _controller = TextEditingController();
  bool _loading = false;
  Map<String, dynamic>? _parsed;
  String _message = '';

  Future<void> _submit() async {
    if (_controller.text.trim().isEmpty) return;
    setState(() => _loading = true);
    try {
      final res = await ApiService.parseVoiceText(_controller.text.trim());
      setState(() {
        _parsed = res['parsed'];
        _message = res['confirmation_message'] ?? '';
      });
    } catch (e) {
      setState(() => _message = 'خطا: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _confirm() async {
    if (_parsed == null) return;
    setState(() => _loading = true);
    try {
      await ApiService.confirmTransaction(_parsed!);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('تراکنش ثبت شد')));
        Navigator.pop(context);
      }
    } catch (e) {
      setState(() => _message = 'خطا در ثبت: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ثبت دستی تراکنش')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          TextField(
            controller: _controller,
            maxLines: 3,
            textDirection: TextDirection.rtl,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              hintText: 'مثال: از احمدی ۵ میلیون تومان خرید کردم بابت تدارکات',
            ),
          ),
          const SizedBox(height: 12),
          FilledButton(onPressed: _loading ? null : _submit, child: const Text('بررسی با هوش مصنوعی')),
          const SizedBox(height: 16),
          if (_loading) const CircularProgressIndicator(),
          if (_message.isNotEmpty && !_loading)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Text(_message),
              ),
            ),
          if (_parsed != null && _parsed!['needs_clarification'] != true && !_loading)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: FilledButton.icon(
                onPressed: _confirm,
                icon: const Icon(Icons.check),
                label: const Text('تایید و ثبت نهایی'),
              ),
            ),
        ]),
      ),
    );
  }
}
