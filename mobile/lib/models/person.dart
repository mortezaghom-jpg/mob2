class Person {
  final int? id;
  final String name;
  final String type;
  final String? phone;
  final String? city;
  final int balance; // مثبت = او به ما بدهکار است، منفی = ما به او بدهکاریم
  final int totalPurchases;
  final int totalPayments;
  final String? lastTransactionAt;

  Person({
    this.id,
    required this.name,
    this.type = 'person',
    this.phone,
    this.city,
    this.balance = 0,
    this.totalPurchases = 0,
    this.totalPayments = 0,
    this.lastTransactionAt,
  });

  factory Person.fromApiJson(Map<String, dynamic> json) => Person(
        id: json['id'] as int?,
        name: json['name'] as String,
        type: json['type'] as String? ?? 'person',
        balance: json['balance'] as int? ?? 0,
        totalPurchases: json['total_purchases'] as int? ?? 0,
        totalPayments: json['total_payments'] as int? ?? 0,
        lastTransactionAt: json['last_transaction_at'] as String?,
      );

  String get balanceLabel {
    if (balance > 0) return 'طلبکار: ${balance.abs()} تومان';
    if (balance < 0) return 'بدهکار: ${balance.abs()} تومان';
    return 'تسویه';
  }
}
