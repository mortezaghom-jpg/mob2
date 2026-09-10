import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/db_helper.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});
  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  List<dynamic> _items = [];
  bool _offline = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.transactions();
      setState(() {
        _items = data;
        _offline = false;
      });
      for (final t in data) {
        await DbHelper.instance.cacheTransaction({
          'server_id': t['id'],
          'type': t['type'],
          'person_id': t['person_id'],
          'amount': t['amount'],
          'description': t['description'],
          'jalali_date': t['jalali_date'],
          'utc_date': t['utc_date'],
          'status': t['status'],
        });
      }
    } catch (_) {
      final cached = await DbHelper.instance.getCachedTransactions();
      setState(() {
        _items = cached;
        _offline = true;
      });
    }
  }

  IconData _iconFor(String type) {
    switch (type) {
      case 'purchase':
        return Icons.shopping_cart;
      case 'payment':
        return Icons.payments;
      case 'settlement':
        return Icons.handshake;
      default:
        return Icons.receipt_long;
    }
  }

  String _typeLabel(String type) {
    switch (type) {
      case 'purchase':
        return 'خرید';
      case 'payment':
        return 'پرداخت';
      case 'settlement':
        return 'تسویه';
      default:
        return type;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('تراکنش‌ها')),
      body: Column(children: [
        if (_offline)
          Container(
            width: double.infinity,
            color: Colors.orange.shade50,
            padding: const EdgeInsets.all(8),
            child: const Text('حالت آفلاین - اطلاعات ذخیره‌شده محلی نمایش داده می‌شود',
                textAlign: TextAlign.center),
          ),
        Expanded(
          child: RefreshIndicator(
            onRefresh: _load,
            child: _items.isEmpty
                ? const Center(child: Text('هنوز تراکنشی ثبت نشده'))
                : ListView.builder(
                    itemCount: _items.length,
                    itemBuilder: (context, i) {
                      final t = _items[i];
                      return ListTile(
                        leading: Icon(_iconFor(t['type'])),
                        title: Text('${_typeLabel(t['type'])} - ${t['amount']} تومان'),
                        subtitle: Text('${t['description'] ?? ''} | ${t['jalali_date']}'),
                      );
                    },
                  ),
          ),
        ),
      ]),
    );
  }
}
