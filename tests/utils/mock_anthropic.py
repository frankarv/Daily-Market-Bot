class MockAnthropic:
    class messages:
        @staticmethod
        def create(*args, **kwargs):
            # Mimic Anthropic response structure used in your routers
            return type(
                "Resp",
                (),
                {
                    "content": [
                        type("TextObj", (), {"text": "Mock AI commentary for testing."})
                    ]
                },
            )
