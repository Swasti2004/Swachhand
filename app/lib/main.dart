import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const SwachhandApp());
}

class SwachhandApp extends StatelessWidget {
  const SwachhandApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Swachhand',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E4633), // Spruce green
          primary: const Color(0xFF1E4633),
          secondary: const Color(0xFFE89A3C), // Trail blaze orange
        ),
        useMaterial3: true,
      ),
      home: const PlanningScreen(),
    );
  }
}

class PlanningScreen extends StatefulWidget {
  const PlanningScreen({super.key});

  @override
  State<PlanningScreen> createState() => _PlanningScreenState();
}

class _PlanningScreenState extends State<PlanningScreen> {
  double _minutes = 45;
  String _energy = 'medium';
  final TextEditingController _placeController = TextEditingController(text: 'Delhi');
  final TextEditingController _apiUrlController = TextEditingController(text: 'http://10.0.2.2:8000');
  
  bool _isLoading = false;
  String? _errorMessage;
  Map<String, dynamic>? _result;

  Future<void> _fetchSuggestions() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _result = null;
    });

    try {
      final base = _apiUrlController.text.trim();
      final uri = Uri.parse('$base/api/suggest');
      
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'place': _placeController.text.trim(),
          'minutes': _minutes.round(),
          'energy': _energy,
          'interests': ['quiet', 'greenery'],
        }),
      );

      if (response.statusCode == 200) {
        setState(() {
          _result = jsonDecode(response.body);
          _isLoading = false;
        });
      } else {
        final err = jsonDecode(response.body);
        setState(() {
          _errorMessage = err['detail'] ?? 'Failed to retrieve suggestions.';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Network connection error: could not reach backend.';
        _isLoading = false;
      });
    }
  }

  Future<void> _recordFeedback(String action, String placeId) async {
    try {
      final base = _apiUrlController.text.trim();
      final uri = Uri.parse('$base/api/feedback');
      await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'action': action,
          'place_id': placeId,
          'minutes': _minutes.round(),
          'energy': _energy,
        }),
      );
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Activity logged ($action). Bandit updated!')),
      );
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Swachhand'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Notice
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: const Text(
                'Notice: Swachhand offers physical lifestyle breaks. It is not medical advice.',
                style: TextStyle(fontSize: 12, color: Colors.black87),
              ),
            ),
            const SizedBox(height: 16),

            // Time Free Slider
            Text('Time Available: ${_minutes.round()} minutes',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            Slider(
              value: _minutes,
              min: 15,
              max: 180,
              divisions: 33,
              label: '${_minutes.round()} min',
              onChanged: (val) => setState(() => _minutes = val),
            ),
            const SizedBox(height: 12),

            // Energy Level
            const Text('Energy Level:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'low', label: Text('Low')),
                ButtonSegment(value: 'medium', label: Text('Medium')),
                ButtonSegment(value: 'high', label: Text('High')),
              ],
              selected: {_energy},
              onSelectionChanged: (set) => setState(() => _energy = set.first),
            ),
            const SizedBox(height: 16),

            // Location Input
            TextField(
              controller: _placeController,
              decoration: const InputDecoration(
                labelText: 'Location (Town or City)',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.location_on),
              ),
            ),
            const SizedBox(height: 12),

            // Server URL
            TextField(
              controller: _apiUrlController,
              decoration: const InputDecoration(
                labelText: 'Backend Server URL',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.dns),
                helperText: 'Use http://10.0.2.2:8000 for Android emulator or your LAN IP for phone.',
              ),
            ),
            const SizedBox(height: 16),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _fetchSuggestions,
                icon: const Icon(Icons.nature_people),
                label: Text(_isLoading ? 'Ranking Outdoors...' : 'Find Somewhere Outside'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
            const SizedBox(height: 16),

            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Text(_errorMessage!, style: TextStyle(color: Colors.red.shade800)),
              ),

            // Results Section
            if (_result != null) ...[
              const Divider(height: 32),
              Text(
                'Weather: ${_result!['weather']?['summary'] ?? ''} (${_result!['weather']?['temperature_c']}°C)',
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 12),
              const Text('Recommended Outings:', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),

              ...((_result!['suggestions'] as List<dynamic>?) ?? []).map((sugg) {
                return Card(
                  margin: const EdgeInsets.symmetric(vertical: 8),
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(14.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                sugg['place']?['name'] ?? 'Outdoor Spot',
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                            ),
                            Chip(
                              label: Text('${sugg['place']?['category']}'),
                              visualDensity: VisualDensity.compact,
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(sugg['activity'] ?? '', style: const TextStyle(fontWeight: FontWeight.w500)),
                        const SizedBox(height: 4),
                        Text(sugg['reason'] ?? '', style: const TextStyle(color: Colors.black87, fontSize: 13)),
                        const SizedBox(height: 8),
                        Text('Walk: ${sugg['place']?['walk_minutes']} min each way • Stay: ${sugg['duration_minutes']} min',
                            style: const TextStyle(fontSize: 12, color: Colors.black54)),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            OutlinedButton.icon(
                              onPressed: () => _recordFeedback('done', sugg['place']['id']),
                              icon: const Icon(Icons.check, size: 16),
                              label: const Text('I Went'),
                            ),
                            const SizedBox(width: 8),
                            TextButton.icon(
                              onPressed: () => _recordFeedback('skipped', sugg['place']['id']),
                              icon: const Icon(Icons.close, size: 16),
                              label: const Text('Skip'),
                            ),
                          ],
                        )
                      ],
                    ),
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }
}
