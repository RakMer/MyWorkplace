import 'package:flutter/material.dart';

void main() {
  runApp(const AkaryakitApp());
}

class AkaryakitApp extends StatelessWidget {
  const AkaryakitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Akaryakıt Fiyatları',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

// ============================================================================
// VERİ MODELİ
// ============================================================================

class FuelPrice {
  final String companyName;
  final double gasPrice;
  final double dieselPrice;
  final String logoUrl;

  FuelPrice({
    required this.companyName,
    required this.gasPrice,
    required this.dieselPrice,
    required this.logoUrl,
  });
}

// ============================================================================
// SAHTE VERİ
// ============================================================================

class FuelDataService {
  static List<FuelPrice> getFuelPrices() {
    return [
      FuelPrice(
        companyName: 'Shell',
        gasPrice: 43.85,
        dieselPrice: 44.92,
        logoUrl: 'https://logo.clearbit.com/shell.com',
      ),
      FuelPrice(
        companyName: 'Opet',
        gasPrice: 43.45,
        dieselPrice: 44.55,
        logoUrl: 'https://logo.clearbit.com/opet.com.tr',
      ),
      FuelPrice(
        companyName: 'Petrol Ofisi',
        gasPrice: 43.95,
        dieselPrice: 45.15,
        logoUrl: 'https://logo.clearbit.com/po.com.tr',
      ),
      FuelPrice(
        companyName: 'BP',
        gasPrice: 43.25,
        dieselPrice: 44.35,
        logoUrl: 'https://logo.clearbit.com/bp.com',
      ),
      FuelPrice(
        companyName: 'Total',
        gasPrice: 44.15,
        dieselPrice: 45.25,
        logoUrl: 'https://logo.clearbit.com/total.com',
      ),
      FuelPrice(
        companyName: 'Lukoil',
        gasPrice: 43.65,
        dieselPrice: 44.75,
        logoUrl: 'https://logo.clearbit.com/lukoil.com',
      ),
    ];
  }
}

// ============================================================================
// DURUM YÖNETİMİ (Basit State Service)
// ============================================================================

class AppState extends ChangeNotifier {
  String _selectedCity = 'İstanbul';

  String get selectedCity => _selectedCity;

  void setCity(String city) {
    _selectedCity = city;
    notifyListeners();
  }
}

final appState = AppState();

// ============================================================================
// ANA SAYFA (HomeScreen)
// ============================================================================

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final List<FuelPrice> fuelPrices = FuelDataService.getFuelPrices();

  @override
  void initState() {
    super.initState();
    appState.addListener(_updateState);
  }

  @override
  void dispose() {
    appState.removeListener(_updateState);
    super.dispose();
  }

  void _updateState() {
    setState(() {});
  }

  void _navigateToSettings() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const SettingsScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Akaryakıt Fiyatları'),
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          actions: [
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: _navigateToSettings,
            ),
          ],
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Benzin Fiyatları', icon: Icon(Icons.local_gas_station)),
              Tab(text: 'Motorin Fiyatları', icon: Icon(Icons.local_shipping)),
            ],
          ),
        ),
        body: Column(
          children: [
            // İl Göstergesi
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
              color: Colors.blue.shade50,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.location_on, color: Colors.blue, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    appState.selectedCity,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.blue,
                    ),
                  ),
                ],
              ),
            ),
            // Tab Views
            Expanded(
              child: TabBarView(
                children: [
                  _buildFuelList(fuelPrices, isGasoline: true),
                  _buildFuelList(fuelPrices, isGasoline: false),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFuelList(List<FuelPrice> prices, {required bool isGasoline}) {
    // Fiyatları al ve min/max hesapla
    final currentPrices = prices.map((p) => isGasoline ? p.gasPrice : p.dieselPrice).toList();
    final minPrice = currentPrices.reduce((a, b) => a < b ? a : b);
    final maxPrice = currentPrices.reduce((a, b) => a > b ? a : b);

    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: prices.length,
      itemBuilder: (context, index) {
        final item = prices[index];
        final price = isGasoline ? item.gasPrice : item.dieselPrice;
        final isMinPrice = price == minPrice;
        final isMaxPrice = price == maxPrice;

        return Card(
          elevation: 2,
          margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
            leading: CircleAvatar(
              backgroundColor: Colors.grey.shade200,
              child: Icon(
                Icons.local_gas_station,
                color: Colors.blue.shade700,
              ),
            ),
            title: Text(
              item.companyName,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: isMinPrice
                    ? Colors.green.shade50
                    : isMaxPrice
                        ? Colors.red.shade50
                        : Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: isMinPrice
                      ? Colors.green
                      : isMaxPrice
                          ? Colors.red
                          : Colors.grey.shade300,
                  width: 2,
                ),
              ),
              child: Text(
                '₺${price.toStringAsFixed(2)}',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: isMinPrice
                      ? Colors.green.shade700
                      : isMaxPrice
                          ? Colors.red.shade700
                          : Colors.black87,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

// ============================================================================
// AYARLAR EKRANI (SettingsScreen)
// ============================================================================

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final List<String> cities = [
    'Adana',
    'Adıyaman',
    'Afyonkarahisar',
    'Ağrı',
    'Aksaray',
    'Amasya',
    'Ankara',
    'Antalya',
    'Ardahan',
    'Artvin',
    'Aydın',
    'Balıkesir',
    'Bartın',
    'Batman',
    'Bayburt',
    'Bilecik',
    'Bingöl',
    'Bitlis',
    'Bolu',
    'Burdur',
    'Bursa',
    'Çanakkale',
    'Çankırı',
    'Çorum',
    'Denizli',
    'Diyarbakır',
    'Düzce',
    'Edirne',
    'Elazığ',
    'Erzincan',
    'Erzurum',
    'Eskişehir',
    'Gaziantep',
    'Giresun',
    'Gümüşhane',
    'Hakkari',
    'Hatay',
    'Iğdır',
    'Isparta',
    'İstanbul',
    'İzmir',
    'Kahramanmaraş',
    'Karabük',
    'Karaman',
    'Kars',
    'Kastamonu',
    'Kayseri',
    'Kırıkkale',
    'Kırklareli',
    'Kırşehir',
    'Kilis',
    'Kocaeli',
    'Konya',
    'Kütahya',
    'Malatya',
    'Manisa',
    'Mardin',
    'Mersin',
    'Muğla',
    'Muş',
    'Nevşehir',
    'Niğde',
    'Ordu',
    'Osmaniye',
    'Rize',
    'Sakarya',
    'Samsun',
    'Siirt',
    'Sinop',
    'Sivas',
    'Şanlıurfa',
    'Şırnak',
    'Tekirdağ',
    'Tokat',
    'Trabzon',
    'Tunceli',
    'Uşak',
    'Van',
    'Yalova',
    'Yozgat',
    'Zonguldak',
  ];

  String selectedCity = appState.selectedCity;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ayarlar'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              'İl Seçimi',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(
              'Akaryakıt fiyatlarını görmek istediğiniz ili seçiniz:',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.builder(
              itemCount: cities.length,
              itemBuilder: (context, index) {
                final city = cities[index];
                final isSelected = city == selectedCity;

                return RadioListTile<String>(
                  title: Text(
                    city,
                    style: TextStyle(
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                  value: city,
                  groupValue: selectedCity,
                  activeColor: Colors.blue,
                  onChanged: (value) {
                    setState(() {
                      selectedCity = value!;
                    });
                  },
                );
              },
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: () {
                appState.setCity(selectedCity);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('İl "$selectedCity" olarak güncellendi'),
                    duration: const Duration(seconds: 2),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
              child: const Text(
                'Kaydet',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
