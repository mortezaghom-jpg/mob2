import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import '../services/api_service.dart';

/// معماری این صفحه دقیقاً همان چیزی است که در الزامات پروژه خواسته شده:
/// Voice -> Speech To Text -> AI (Backend) -> Structured JSON -> نمایش برای تایید -> Accounting Engine
class VoiceEntryScreen extends StatefulWidget {
  const VoiceEntryScreen({super.key});
  @override
  State<VoiceEntryScreen> createState() => _VoiceEntryScreenState();
}

enum _Stage { idle, listening, processing, confirming, done, error }

class _VoiceEntryScreenState extends State<VoiceEntryScreen> {
  final stt.SpeechToText _speech = stt.SpeechToText();
  _Stage _stage = _Stage.idle;
  String _recognizedText = '';
  Map<String, dynamic>? _parsed;
  String _confirmationMessage = '';
  String _errorText = '';

  Future<void> _startListening() async {
    final available = await _speech.initialize(
      onError: (e) => setState(() {
        _stage = _Stage.error;
        _errorText = 'میکروفون در دسترس نیست: ${e.errorMsg}';
      }),
    );
    if (!available) {
      setState(() {
        _stage = _Stage.error;
        _errorText = 'دسترسی به میکروفون یا موتور تشخیص گفتار فارسی ممکن نشد.';
      });
      return;
    }
    setState(() {
      _stage = _Stage.listening;
      _recognizedText = '';
    });
    _speech.listen(
      localeId: 'fa_IR',
      onResult: (result) {
        setState(() => _recognizedText = result.recognizedWords);
        if (result.finalResult) {
          _speech.stop();
          _sendToAi(result.recognizedWords);
        }
      },
    );
  }

  Future<void> _sendToAi(String text) async {
    if (text.trim().isEmpty) {
      setState(() => _stage = _Stage.idle);
      return;
    }
    setState(() => _stage = _Stage.processing);
    try {
      final res = await ApiService.parseVoiceText(text);
      setState(() {
        _parsed = res['parsed'] as Map<String, dynamic>;
        _confirmationMessage = res['confirmation_message'] as String? ?? '';
        _stage = _Stage.confirming;
      });
    } catch (e) {
      setState(() {
        _stage = _Stage.error;
        _errorText = e.toString();
      });
    }
  }

  Future<void> _confirm() async {
    if (_parsed == null) return;
    setState(() => _stage = _Stage.processing);
    try {
      await ApiService.confirmTransaction(_parsed!);
      setState(() => _stage = _Stage.done);
    } catch (e) {
      setState(() {
        _stage = _Stage.error;
        _errorText = e.toString();
      });
    }
  }

  void _reject() {
    setState(() {
      _stage = _Stage.idle;
      _parsed = null;
      _recognizedText = '';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ثبت صوتی تراکنش')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Center(child: _buildBody()),
      ),
    );
  }

  Widget _buildBody() {
    switch (_stage) {
      case _Stage.idle:
        return Column(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.mic_none, size: 96, color: Colors.teal),
          const SizedBox(height: 16),
          const Text('برای ثبت تراکنش صحبت کنید', style: TextStyle(fontSize: 18)),
          const SizedBox(height: 8),
          const Text('مثال: «از احمدی ۵ میلیون تومان خرید کردم بابت تدارکات»',
              textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
          const SizedBox(height: 32),
          FilledButton.icon(
            onPressed: _startListening,
            icon: const Icon(Icons.mic),
            label: const Text('شروع صحبت'),
            style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16)),
          ),
        ]);
      case _Stage.listening:
        return Column(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.mic, size: 96, color: Colors.red),
          const SizedBox(height: 16),
          const Text('در حال شنیدن...', style: TextStyle(fontSize: 18)),
          const SizedBox(height: 16),
          Text(_recognizedText, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16)),
        ]);
      case _Stage.processing:
        return const Column(mainAxisSize: MainAxisSize.min, children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('در حال پردازش با هوش مصنوعی...'),
        ]);
      case _Stage.confirming:
        return Column(mainAxisSize: MainAxisSize.min, children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(_confirmationMessage, style: const TextStyle(fontSize: 16, height: 1.8)),
            ),
          ),
          const SizedBox(height: 24),
          if (_parsed?['needs_clarification'] == true)
            FilledButton(onPressed: _reject, child: const Text('باشه، دوباره می‌گویم'))
          else
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              OutlinedButton(onPressed: _reject, child: const Text('خیر')),
              const SizedBox(width: 16),
              FilledButton(onPressed: _confirm, child: const Text('بله، ثبت شود')),
            ]),
        ]);
      case _Stage.done:
        return Column(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.check_circle, size: 96, color: Colors.green),
          const SizedBox(height: 16),
          const Text('تراکنش با موفقیت ثبت شد', style: TextStyle(fontSize: 18)),
          const SizedBox(height: 24),
          FilledButton(onPressed: () => Navigator.pop(context), child: const Text('بازگشت به داشبورد')),
        ]);
      case _Stage.error:
        return Column(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.error_outline, size: 96, color: Colors.red),
          const SizedBox(height: 16),
          Text(_errorText, textAlign: TextAlign.center),
          const SizedBox(height: 24),
          FilledButton(onPressed: () => setState(() => _stage = _Stage.idle), child: const Text('تلاش دوباره')),
        ]);
    }
  }
}
