import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as p;

/// دیتابیس محلی SQLite - برای مشاهده اطلاعات حتی بدون اینترنت (Offline-first).
/// ساختار جدول‌ها مطابق database/schema.sql است.
/// این کلاس رکوردهایی را که از Backend دریافت می‌شوند کش می‌کند، و همچنین
/// تراکنش‌های ثبت‌شده وقتی آفلاین بودیم را تا اتصال بعدی نگه می‌دارد (sync_pending).
class DbHelper {
  DbHelper._();
  static final DbHelper instance = DbHelper._();
  Database? _db;

  Future<Database> get database async {
    _db ??= await _initDb();
    return _db!;
  }

  Future<Database> _initDb() async {
    final dbPath = await getDatabasesPath();
    final path = p.join(dbPath, 'tanakhah.db');
    return openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        // این DDL معادل ساده‌شده database/schema.sql برای موبایل است.
        await db.execute('''
          CREATE TABLE persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'person',
            balance INTEGER DEFAULT 0,
            total_purchases INTEGER DEFAULT 0,
            total_payments INTEGER DEFAULT 0,
            last_transaction_at TEXT
          )
        ''');
        await db.execute('''
          CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
          )
        ''');
        await db.execute('''
          CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER,
            type TEXT NOT NULL,
            person_id INTEGER,
            category TEXT,
            amount INTEGER NOT NULL,
            description TEXT,
            jalali_date TEXT NOT NULL,
            utc_date TEXT NOT NULL,
            status TEXT DEFAULT 'confirmed',
            source TEXT DEFAULT 'manual',
            sync_pending INTEGER DEFAULT 0
          )
        ''');
        await db.execute('''
          CREATE TABLE settings (
            key TEXT PRIMARY KEY,
            value TEXT
          )
        ''');
      },
    );
  }

  Future<int> cacheTransaction(Map<String, dynamic> row) async {
    final db = await database;
    return db.insert('transactions', row, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Map<String, dynamic>>> getCachedTransactions({int limit = 50}) async {
    final db = await database;
    return db.query('transactions', orderBy: 'id DESC', limit: limit);
  }

  Future<List<Map<String, dynamic>>> getPendingSyncTransactions() async {
    final db = await database;
    return db.query('transactions', where: 'sync_pending = 1');
  }

  Future<void> markSynced(int localId, int serverId) async {
    final db = await database;
    await db.update('transactions', {'sync_pending': 0, 'server_id': serverId},
        where: 'id = ?', whereArgs: [localId]);
  }

  Future<String?> getSetting(String key) async {
    final db = await database;
    final rows = await db.query('settings', where: 'key = ?', whereArgs: [key]);
    return rows.isEmpty ? null : rows.first['value'] as String?;
  }

  Future<void> setSetting(String key, String value) async {
    final db = await database;
    await db.insert('settings', {'key': key, 'value': value},
        conflictAlgorithm: ConflictAlgorithm.replace);
  }
}
