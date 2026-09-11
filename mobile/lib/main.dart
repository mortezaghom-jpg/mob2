import 'package:flutter/material.dart';
import 'screens/dashboard_screen.dart';
import 'screens/voice_entry_screen.dart';
import 'screens/manual_entry_screen.dart';
import 'screens/transactions_screen.dart';
import 'screens/persons_screen.dart';
import 'screens/categories_screen.dart';
import 'screens/reports_screen.dart';
import 'screens/settings_screen.dart';
import 'services/db_helper.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await DbHelper.instance.database; // ساخت/باز کردن دیتابیس SQLite محلی در استارت آپ
  runApp(const HesabyarApp());
}

class HesabyarApp extends StatelessWidget {
  const HesabyarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'حساب‌یار هوشمند تنخواه',
      debugShowCheckedModeBanner: false,
      locale: const Locale('fa', 'IR'),
            localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('fa', 'IR')],
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: const Color(0xFF1E6F5C),
       // fontFamily: 'Vazirmatn', // فونت فارسی - فایل را در assets قرار دهید
        brightness: Brightness.light,
      ),
      builder: (context, child) {
        // اجبار جهت راست‌به‌چپ برای کل اپلیکیشن
        return Directionality(textDirection: TextDirection.rtl, child: child!);
      },
      initialRoute: '/',
      routes: {
        '/': (_) => const DashboardScreen(),
        '/voice': (_) => const VoiceEntryScreen(),
        '/manual': (_) => const ManualEntryScreen(),
        '/transactions': (_) => const TransactionsScreen(),
        '/persons': (_) => const PersonsScreen(),
        '/categories': (_) => const CategoriesScreen(),
        '/reports': (_) => const ReportsScreen(),
        '/settings': (_) => const SettingsScreen(),
      },
    );
  }
}
