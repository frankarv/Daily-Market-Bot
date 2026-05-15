class MockAnthropic:
    class messages:
        @staticmethod
        def create(*args, **kwargs):
            return type("obj", (), {
                "content": [type("t", (), {"text": "Mock commentary"})]
            })
