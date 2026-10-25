import 'package:flutter_test/flutter_test.dart';
import 'package:swachhand/main.dart';

void main() {
  testWidgets('Swachhand app smoke and title test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const SwachhandApp());

    // Verify title and main elements are rendered.
    expect(find.text('Swachhand'), findsOneWidget);
    expect(find.text('Find Somewhere Outside'), findsOneWidget);
  });
}
