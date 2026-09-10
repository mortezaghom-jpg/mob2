class AppTransaction {
  final int? id;
  final String type; // purchase | payment | settlement
  final int? personId;
  final String? personName;
  final int amount;
  final String? description;
  final String jalaliDate;
  final String utcDate;
  final String? category;
  final String status; // pending_confirmation | confirmed | cancelled
  final String source; // manual | voice

  AppTransaction({
    this.id,
    required this.type,
    this.personId,
    this.personName,
    required this.amount,
    this.description,
    required this.jalaliDate,
    required this.utcDate,
    this.category,
    this.status = 'confirmed',
    this.source = 'manual',
  });

  Map<String, dynamic> toMap() => {
        'id': id,
        'type': type,
        'person_id': personId,
        'amount': amount,
        'description': description,
        'jalali_date': jalaliDate,
        'utc_date': utcDate,
        'status': status,
        'source': source,
      };

  factory AppTransaction.fromMap(Map<String, dynamic> map) => AppTransaction(
        id: map['id'] as int?,
        type: map['type'] as String,
        personId: map['person_id'] as int?,
        amount: map['amount'] as int,
        description: map['description'] as String?,
        jalaliDate: map['jalali_date'] as String,
        utcDate: map['utc_date'] as String,
        status: map['status'] as String? ?? 'confirmed',
        source: map['source'] as String? ?? 'manual',
      );

  factory AppTransaction.fromApiJson(Map<String, dynamic> json) => AppTransaction(
        id: json['id'] as int?,
        type: json['type'] as String,
        personId: json['person_id'] as int?,
        amount: json['amount'] as int,
        description: json['description'] as String?,
        jalaliDate: json['jalali_date'] as String,
        utcDate: json['utc_date'] as String,
        status: json['status'] as String? ?? 'confirmed',
      );
}
