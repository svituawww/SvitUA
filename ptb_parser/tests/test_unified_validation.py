#!/usr/bin/env python3
"""
Test script for Unified Validation System - id_part6 Implementation
Demonstrates the unified validation functionality
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import from scripts
sys.path.append(str(Path(__file__).parent.parent))

from scripts.tech_tag_collector import TechHTMLCollector

def test_unified_validation():
    """Test the unified validation system."""
    print("🧪 Testing Unified Validation System - id_part6")
    print("=" * 60)
    
    # Initialize the collector
    collector = TechHTMLCollector("json/tech_tag_config.json")
    
    # Test file
    test_file = "input/test1.html"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📄 Testing with file: {test_file}")
    
    try:
        # Run comprehensive validation
        unified_report = collector.run_comprehensive_validation(test_file)
        
        # Display results
        print("\n📊 Unified Validation Results:")
        print(f"   Overall Status: {unified_report.get('overall_validation_status', 'UNKNOWN')}")
        print(f"   Overall Score: {unified_report.get('overall_validation_score', 0.0):.2f}")
        
        # Display validation summary
        validation_summary = unified_report.get("validation_summary", {})
        print(f"   Validation Coverage: {validation_summary.get('validation_coverage', 0.0):.2f}")
        print(f"   Passed Validations: {validation_summary.get('passed_validations', 0)}/{validation_summary.get('total_validation_types', 0)}")
        
        # Display cross-validation analysis
        cross_analysis = unified_report.get("cross_validation_analysis", {})
        print(f"\n🔗 Cross-Validation Analysis:")
        print(f"   Symbol-Comment Correlation: {cross_analysis.get('symbol_comment_correlation', 0.0):.2f}")
        print(f"   Element-Symbol Alignment: {cross_analysis.get('element_symbol_alignment', 0.0):.2f}")
        print(f"   Overall Structure Integrity: {cross_analysis.get('overall_structure_integrity', 0.0):.2f}")
        
        # Display detailed validation results
        validation_details = unified_report.get("validation_details", {})
        
        print(f"\n📋 Detailed Validation Results:")
        
        # Comment validation
        comment_val = validation_details.get("comment_validation", {})
        print(f"   Comment Validation: {comment_val.get('comment_validation_status', 'UNKNOWN')}")
        print(f"     Score: {comment_val.get('comment_consistency_score', 0.0):.2f}")
        print(f"     Pairs: {comment_val.get('valid_comment_pairs', 0)}/{comment_val.get('total_comment_symbols', 0)}")
        
        # Symbol validation
        symbol_val = validation_details.get("symbol_validation", {})
        print(f"   Symbol Validation: {symbol_val.get('symbol_validation_status', 'UNKNOWN')}")
        print(f"     Score: {symbol_val.get('symbol_consistency_score', 0.0):.2f}")
        print(f"     Pairs: {symbol_val.get('valid_pairs', 0)}/{symbol_val.get('total_symbols', 0)}")
        
        # Element sequence validation
        element_val = validation_details.get("element_sequence_validation", {})
        print(f"   Element Sequence Validation: {element_val.get('sequence_validation_status', 'UNKNOWN')}")
        print(f"     Score: {element_val.get('sequence_consistency_score', 0.0):.2f}")
        print(f"     Valid Pairs: {element_val.get('validated_pairs', 0)}/{element_val.get('total_elements', 0)-1}")
        
        # Show sequence errors if any
        sequence_errors = element_val.get("sequence_errors", [])
        if sequence_errors:
            print(f"\n⚠️  Sequence Errors Found: {len(sequence_errors)}")
            for i, error in enumerate(sequence_errors[:3]):  # Show first 3 errors
                print(f"   Error {i+1}: Gap/Overlap of {error.get('gap_or_overlap', 0)} positions")
                print(f"     Between elements {error.get('current_element_id')} and {error.get('next_element_id')}")
        
        print(f"\n✅ Test completed successfully!")
        print(f"📁 Results saved to: json/unified_validation.json")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_unified_validation() 