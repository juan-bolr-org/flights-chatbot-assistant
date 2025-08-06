#!/usr/bin/env python3
"""
Debug script to test middleware path exclusion logic
"""
import sys
import os
sys.path.insert(0, 'src')

from middleware.auth import JWTAuthMiddleware

def test_middleware():
    # Test the exact same logic as the failing test
    excluded_paths = ['/health', '/docs', '/users/login', '/public/*']
    middleware = JWTAuthMiddleware(app=None, excluded_paths=excluded_paths)

    print('Testing excluded paths:')
    test_cases = [
        ('/health', True),
        ('/docs', True), 
        ('/users/login', True),
        ('/public/anything', True),
        ('/public/test/nested', True),
        ('/users/me', False),
        ('/flights', False)
    ]

    all_passed = True
    for path, expected in test_cases:
        result = middleware._is_path_excluded(path)
        passed = result == expected
        all_passed = all_passed and passed
        print(f'{path}: {result} (expected {expected}) - {"✓" if passed else "✗"}')

    print(f'\nAll tests passed: {all_passed}')

    # Debug the patterns
    print('\nCompiled patterns:')
    for i, pattern_obj in enumerate(middleware.excluded_patterns):
        print(f'{excluded_paths[i]} -> {pattern_obj.pattern}')
        
    # Test pattern matching directly
    print('\nTesting /public/* pattern directly:')
    public_pattern = None
    for i, path in enumerate(excluded_paths):
        if path == '/public/*':
            public_pattern = middleware.excluded_patterns[i]
            break
    
    if public_pattern:
        test_paths = ['/public/anything', '/public/test/nested', '/public/', '/public', '/users/me']
        for path in test_paths:
            match = public_pattern.match(path)
            print(f'Pattern {public_pattern.pattern} matches {path}: {match is not None}')

if __name__ == '__main__':
    test_middleware()
