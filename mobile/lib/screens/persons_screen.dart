import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/person.dart';

class PersonsScreen extends StatefulWidget {
  const PersonsScreen({super.key});
  @override
  State<PersonsScreen> createState() => _PersonsScreenState();
}

class _PersonsScreenState extends State<PersonsScreen> {
  List<Person> _persons = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await ApiService.persons();
      setState(() {
        _persons = data.map((e) => Person.fromApiJson(e)).toList();
        _error = null;
      });
    } catch (e) {
      setState(() => _error = 'اتصال برقرار نشد. لطفاً تنظیمات آدرس Backend را بررسی کنید.');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('طرف حساب‌ها')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.builder(
                    itemCount: _persons.length,
                    itemBuilder: (context, i) {
                      final p = _persons[i];
                      final color = p.balance < 0 ? Colors.red : (p.balance > 0 ? Colors.green : Colors.grey);
                      return ListTile(
                        leading: CircleAvatar(child: Text(p.name.isNotEmpty ? p.name[0] : '?')),
                        title: Text(p.name),
                        subtitle: Text('خرید: ${p.totalPurchases} | پرداخت: ${p.totalPayments}'),
                        trailing: Text(p.balanceLabel, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
                      );
                    },
                  ),
                ),
    );
  }
}
