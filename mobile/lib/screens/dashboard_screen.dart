import 'package:flutter/material.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _data;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await ApiService.dashboard();
      setState(() => _data = data);
    } catch (e) {
      setState(() => _error = 'اتصال به سرور برقرار نشد. اطلاعات آفلاین نمایش داده می‌شود.');
    } finally {
      setState(() => _loading = false);
    }
  }

  String _fmt(dynamic v) {
    if (v == null) return '۰';
    final n = v as int;
    return n.toString().replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (m) => ',');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('حساب‌یار هوشمند تنخواه'),
        actions: [
          IconButton(icon: const Icon(Icons.settings), onPressed: () => Navigator.pushNamed(context, '/settings')),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_error != null)
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(color: Colors.orange.shade50, borderRadius: BorderRadius.circular(8)),
                child: Text(_error!, style: TextStyle(color: Colors.orange.shade900)),
              ),
            if (_loading) const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator())),
            if (_data != null) ...[
              _statCard('موجودی تنخواه', _fmt(_data!['tanakhah_balance']), Icons.account_balance_wallet, Colors.teal),
              Row(children: [
                Expanded(child: _smallStat('مجموع خریدها', _fmt(_data!['total_purchases']))),
                const SizedBox(width: 8),
                Expanded(child: _smallStat('مجموع پرداخت‌ها', _fmt(_data!['total_payments']))),
              ]),
              const SizedBox(height: 8),
              Row(children: [
                Expanded(child: _smallStat('بدهی ما به دیگران', _fmt(_data!['our_debt_to_others']))),
                const SizedBox(width: 8),
                Expanded(child: _smallStat('طلب ما از دیگران', _fmt(_data!['others_debt_to_us']))),
              ]),
              const SizedBox(height: 8),
              Row(children: [
                Expanded(child: _smallStat('هزینه امروز', _fmt(_data!['today_expenses']))),
                const SizedBox(width: 8),
                Expanded(child: _smallStat('هزینه این ماه', _fmt(_data!['month_expenses']))),
              ]),
            ],
            const SizedBox(height: 24),
            _quickLinks(context),
            const SizedBox(height: 100),
          ],
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.pushNamed(context, '/voice').then((_) => _load()),
        icon: const Icon(Icons.mic, size: 28),
        label: const Text('برای ثبت تراکنش صحبت کنید', style: TextStyle(fontSize: 15)),
        backgroundColor: Theme.of(context).colorScheme.primary,
      ),
    );
  }

  Widget _statCard(String title, String value, IconData icon, Color color) {
    return Card(
      color: color.withOpacity(0.08),
      child: ListTile(
        leading: Icon(icon, color: color, size: 32),
        title: Text(title),
        trailing: Text('$value تومان', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      ),
    );
  }

  Widget _smallStat(String title, String value) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: const TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 4),
          Text('$value تومان', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        ]),
      ),
    );
  }

  Widget _quickLinks(BuildContext context) {
    final links = [
      ('ثبت دستی', Icons.edit_note, '/manual'),
      ('تراکنش‌ها', Icons.list_alt, '/transactions'),
      ('طرف حساب‌ها', Icons.people, '/persons'),
      ('دسته‌بندی‌ها', Icons.category, '/categories'),
      ('گزارش‌ها', Icons.bar_chart, '/reports'),
    ];
    return GridView.count(
      crossAxisCount: 3,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 8,
      crossAxisSpacing: 8,
      children: links
          .map((l) => Card(
                child: InkWell(
                  onTap: () => Navigator.pushNamed(context, l.$3),
                  child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                    Icon(l.$2, size: 28),
                    const SizedBox(height: 6),
                    Text(l.$1, style: const TextStyle(fontSize: 12)),
                  ]),
                ),
              ))
          .toList(),
    );
  }
}
