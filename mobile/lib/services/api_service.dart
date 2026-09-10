import 'dart:convert';
import 'package:http/http.dart' as http;
import 'db_helper.dart';

/// این سرویس تنها راه ارتباط اپ اندروید با هوش مصنوعی است.
/// هیچ کلید API در این فایل یا هیچ‌جای دیگر اپلیکیشن وجود ندارد -
/// کلید فقط روی Backend (فایل .env) نگهداری می‌شود.
/// آدرس Backend از تنظیمات کاربر خوانده می‌شود (صفحه تنظیمات).
class ApiService {
  static Future<String> get baseUrl async {
    final saved = await DbHelper.instance.getSetting('backend_url');
    return saved ?? 'http://10.0.2.2:8000'; // پیش‌فرض برای Android Emulator
  }

  static Future<Map<String, dynamic>> parseVoiceText(String text) async {
    final url = Uri.parse('${await baseUrl}/voice/parse');
    final res = await http
        .post(url, headers: {'Content-Type': 'application/json'}, body: jsonEncode({'text': text}))
        .timeout(const Duration(seconds: 20));
    if (res.statusCode != 200) {
      throw ApiException('خطا در ارتباط با سرویس هوش مصنوعی (${res.statusCode})');
    }
    return jsonDecode(utf8.decode(res.bodyBytes));
  }

  static Future<Map<String, dynamic>> confirmTransaction(Map<String, dynamic> parsed) async {
    final url = Uri.parse('${await baseUrl}/voice/confirm');
    final res = await http
        .post(url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'parsed': parsed, 'confirmed': true}))
        .timeout(const Duration(seconds: 20));
    if (res.statusCode != 200) {
      throw ApiException('ثبت تراکنش با خطا مواجه شد (${res.statusCode})');
    }
    return jsonDecode(utf8.decode(res.bodyBytes));
  }

  static Future<Map<String, dynamic>> dashboard() async {
    final url = Uri.parse('${await baseUrl}/reports/dashboard');
    final res = await http.get(url).timeout(const Duration(seconds: 15));
    if (res.statusCode != 200) {
      throw ApiException('عدم دسترسی به داشبورد (${res.statusCode})');
    }
    return jsonDecode(utf8.decode(res.bodyBytes));
  }

  static Future<List<dynamic>> transactions({int limit = 50}) async {
    final url = Uri.parse('${await baseUrl}/transactions?limit=$limit');
    final res = await http.get(url).timeout(const Duration(seconds: 15));
    if (res.statusCode != 200) {
      throw ApiException('عدم دسترسی به تراکنش‌ها (${res.statusCode})');
    }
    return jsonDecode(utf8.decode(res.bodyBytes));
  }

  static Future<List<dynamic>> persons() async {
    final url = Uri.parse('${await baseUrl}/persons');
    final res = await http.get(url).timeout(const Duration(seconds: 15));
    if (res.statusCode != 200) {
      throw ApiException('عدم دسترسی به طرف‌حساب‌ها (${res.statusCode})');
    }
    return jsonDecode(utf8.decode(res.bodyBytes));
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}
