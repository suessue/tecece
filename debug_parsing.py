#!/usr/bin/env python3
"""
Debug script to analyze the parsing issues in _extract_operation_from_key method.
"""

from diff_detector import APISpecDiffDetector

def debug_parsing(key_str):
    """Debug the parsing of a key string."""
    print(f"Debugging: {key_str}")
    print("=" * 50)
    
    # Step 1: Split by ']'
    parts = key_str.split("']")
    print(f"Parts after splitting by \"']\":")
    for i, part in enumerate(parts):
        print(f"  {i}: {repr(part)}")
    
    # Step 2: Look for paths
    print(f"\nLooking for paths (containing \"['/\"):")
    path = None
    for i, part in enumerate(parts):
        has_path = "['/" in part
        print(f"  Part {i}: {repr(part)} -> Contains path? {has_path}")
        if has_path:
            try:
                extracted_path = part.split("['")[1]
                print(f"    Extracted path: {repr(extracted_path)}")
                path = extracted_path
            except IndexError:
                print(f"    Failed to extract path from: {repr(part)}")
    
    # Step 3: Look for HTTP methods - this is where the bug is!
    print(f"\nLooking for HTTP methods:")
    method = None
    http_methods = ['get', 'post', 'put', 'delete', 'options', 'head', 'patch', 'trace']
    for i, part in enumerate(parts):
        print(f"  Part {i}: {repr(part)}")
        for m in http_methods:
            # The current implementation looks for "['{method}']" IN the part
            # But after splitting by "']", this pattern doesn't exist!
            pattern = f"['{m}']"
            found = pattern in part
            print(f"    Checking pattern {repr(pattern)}: {found}")
            if found:
                print(f"    Found method '{m}'")
                method = m
                break
        if method:
            break
    
    # Show what the method SHOULD look for
    print(f"\nWhat the method SHOULD look for:")
    for i, part in enumerate(parts):
        for m in http_methods:
            # Should look for "['method" (without the closing bracket)
            correct_pattern = f"['{m}"
            found = correct_pattern in part
            if found:
                print(f"  Part {i}: {repr(part)} contains correct pattern {repr(correct_pattern)} for method '{m}'")
                if method is None:  # Only set the first one found
                    method = m
    
    print(f"\nFinal result:")
    print(f"  Path: {repr(path)}")
    print(f"  Method: {repr(method)}")
    
    if path and method:
        result = f"{method.upper()} {path}"
        print(f"  Formatted: {repr(result)}")
    else:
        print(f"  Result: None (missing path or method)")
    
    print()

def main():
    """Test various key strings to understand parsing limitations."""
    test_cases = [
        "root['paths']['/users']['get']['summary']",
        "root['paths']['/users']['get']",
        "root['paths']['/api/v1/users']['post']['requestBody']",
        "root['paths']['/simple']['patch']",
    ]
    
    detector = APISpecDiffDetector()
    
    for case in test_cases:
        debug_parsing(case)
        
        # Compare with actual method result
        actual_result = detector._extract_operation_from_key(case)
        print(f"Actual method result: {repr(actual_result)}")
        print("-" * 80)
        print()

if __name__ == "__main__":
    main() 