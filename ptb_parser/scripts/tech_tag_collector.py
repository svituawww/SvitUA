#!/usr/bin/env python3
"""
TECH_HTML Tag Collector - id_part1 Implementation
Dedicated script for TECH_HTML element collection and processing
Extracted from tag_collector.py for focused TECH_HTML processing
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

class TechHTMLCollector:
    def __init__(self, config_file: str = "json/tech_tag_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file not found: {self.config_file}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for TECH_HTML processing."""
        return {
            "input_files": ["input/index_html_.html"],
            "output_database_tech_elements": "json/tech_tag_html_elements.json",
            "output_database_byte": "json/all_openclose_bytes.json",
            "output_database_comment_validation": "json/comment_validation.json",
            "enable_bracket_collection": True,
            "enable_tech_html_collection": True,
            "enable_comment_validation": True,
            "context_length_before_after_bracket": 5,
            "tech_html_settings": {
                "include_body_content": True,
                "include_name_extraction": True,
                "type_classification": True,
                "standard_tags_list": [
                    "html", "head", "body", "title", "meta", "link", "script", "style",
                    "div", "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
                    "ul", "ol", "li", "a", "img", "br", "hr", "table", "tr", "td", "th",
                    "form", "input", "button", "textarea", "select", "option",
                    "nav", "header", "footer", "main", "section", "article", "aside",
                    "figure", "figcaption", "blockquote", "code", "pre", "em", "strong",
                    "b", "i", "u", "s", "mark", "small", "sub", "sup", "del", "ins",
                    "cite", "q", "abbr", "acronym", "address", "time", "data", "var",
                    "samp", "kbd", "output", "progress", "meter", "details", "summary",
                    "dialog", "menu", "menuitem", "command", "keygen", "canvas", "svg",
                    "path", "circle", "rect", "ellipse", "line", "polyline", "polygon",
                    "use", "area", "base", "col", "embed", "param", "source", "track", "wbr"
                ],
                "custom_tag_detection": True,
                "comment_handling": True,
                "doctype_handling": True,
                "closing_tag_recognition": True
            },
            "processing_settings": {
                "max_file_size_mb": 10,
                "encoding": "utf-8",
                "error_handling": "continue",
                "verbose_output": True
            }
        }
    
    def scan_bytes_for_brackets(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan file byte-by-byte for < and > brackets."""
        brackets = []
        bracket_counter = 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pos, char in enumerate(content):
                if char in ['<', '>']:
                    bracket_data = {
                        "id": bracket_counter,
                        "order": bracket_counter,
                        "bracket": char,
                        "pos_in_file": pos
                    }
                    brackets.append(bracket_data)
                    bracket_counter += 1
            
            return brackets
        except Exception as e:
            print(f"❌ Error scanning brackets in {file_path}: {e}")
            return []
    
    def enhance_brackets_with_context(self, brackets: List[Dict[str, Any]], content: str) -> List[Dict[str, Any]]:
        """Enhance brackets with context data (chars_before, chars_after, full_context) and comment detection."""
        context_length = self.config.get("context_length_before_after_bracket", 5)
        enhanced_brackets = []
        
        for bracket in brackets:
            pos = bracket["pos_in_file"]
            bracket_char = bracket["bracket"]
            
            # Calculate context boundaries
            start_before = pos - context_length
            end_before = pos
            start_after = pos + 1
            end_after = pos + 1 + context_length
            
            # Extract chars_before (only existing characters, no padding)
            chars_before = ""
            if start_before >= 0:
                chars_before = content[start_before:end_before]
            else:
                # Handle beginning of file - only use existing characters
                chars_before = content[0:end_before] if end_before > 0 else ""
            
            # Extract chars_after (only existing characters, no padding)
            chars_after = ""
            if start_after < len(content):
                end_after = min(end_after, len(content))
                chars_after = content[start_after:end_after]
            
            # Create full context
            full_context = chars_before + bracket_char + chars_after
            
            # Detect comment type based on context
            type_tech_tag = self.detect_comment_type(bracket_char, chars_before, chars_after)
            
            # Create enhanced bracket data
            enhanced_bracket = {
                "id": bracket["id"],
                "order": bracket["order"],
                "bracket": bracket_char,
                "pos_in_file": pos,
                "chars_5_before": chars_before,
                "chars_5_after": chars_after,
                "type_tech_tag": type_tech_tag,
                "full_context": full_context
            }
            
            enhanced_brackets.append(enhanced_bracket)
        
        # Mark inner comment content after initial comment detection
        enhanced_brackets = self.mark_inner_comment_content(enhanced_brackets)
        
        return enhanced_brackets
    
    def detect_comment_type(self, bracket: str, chars_before: str, chars_after: str) -> str:
        """Detect if bracket is part of a comment opening, closing, or regular tag."""
        # Check for opening comment: bracket == "<" AND chars_5_after[0:3] == "!--"
        if bracket == "<" and len(chars_after) >= 3 and chars_after[0:3] == "!--":
            return "comm_open"
        
        # Check for closing comment: bracket == ">" AND chars_5_before[-2:] == "--"
        if bracket == ">" and len(chars_before) >= 2 and chars_before[-2:] == "--":
            return "comm_close"
        
        # Regular tag
        return "regular"
    
    def mark_inner_comment_content(self, brackets_with_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mark brackets between comment opening and closing as inner comment content."""
        enhanced_brackets = brackets_with_data.copy()
        comment_stack = []
        
        for i, bracket in enumerate(enhanced_brackets):
            if bracket["type_tech_tag"] == "comm_open":
                # Push comment opening to stack
                comment_stack.append({
                    "id": bracket["id"],
                    "pos": bracket["pos_in_file"],
                    "index": i
                })
            elif bracket["type_tech_tag"] == "comm_close":
                if comment_stack:
                    # Found matching comment closing - mark all brackets in between
                    opening = comment_stack.pop()
                    start_index = opening["index"] + 1
                    end_index = i
                    
                    # Mark all brackets between opening and closing as inner_comm_content
                    for j in range(start_index, end_index):
                        if enhanced_brackets[j]["type_tech_tag"] == "regular":
                            enhanced_brackets[j]["type_tech_tag"] = "inner_comm_content"
        
        return enhanced_brackets
    
    def validate_comment_consistency(self, brackets_with_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate comment type consistency and pairing using stack-based approach."""
        validation_results = {
            "total_comment_brackets": 0,
            "comment_opening_brackets": 0,
            "comment_closing_brackets": 0,
            "valid_comment_pairs": 0,
            "orphaned_comment_openings": [],
            "orphaned_comment_closings": [],
            "comment_consistency_score": 0.0,
            "comment_validation_status": "PASSED"
        }
        
        comment_opening_stack = []
        
        for i, bracket in enumerate(brackets_with_data):
            if bracket["type_tech_tag"] == "comm_open":
                validation_results["comment_opening_brackets"] += 1
                validation_results["total_comment_brackets"] += 1
                comment_opening_stack.append({
                    "id": bracket["id"],
                    "pos": bracket["pos_in_file"],
                    "index": i
                })
            elif bracket["type_tech_tag"] == "comm_close":
                validation_results["comment_closing_brackets"] += 1
                validation_results["total_comment_brackets"] += 1
                
                if comment_opening_stack:
                    # Valid comment pair found - pop the matching opening bracket
                    opening = comment_opening_stack.pop()
                    validation_results["valid_comment_pairs"] += 1
                else:
                    # Orphaned comment closing bracket
                    validation_results["orphaned_comment_closings"].append(bracket["id"])
        
        # Check for orphaned comment opening brackets
        for opening in comment_opening_stack:
            validation_results["orphaned_comment_openings"].append(opening["id"])
        
        # Calculate comment consistency score (0.0 to 1.0)
        total_comment_brackets = validation_results["comment_opening_brackets"] + validation_results["comment_closing_brackets"]
        if total_comment_brackets > 0:
            validation_results["comment_consistency_score"] = (validation_results["valid_comment_pairs"] * 2) / total_comment_brackets
        
        # Determine comment validation status
        if (len(validation_results["orphaned_comment_openings"]) == 0 and 
            len(validation_results["orphaned_comment_closings"]) == 0 and
            validation_results["comment_consistency_score"] == 1.0):
            validation_results["comment_validation_status"] = "PASSED"
        else:
            validation_results["comment_validation_status"] = "FAILED"
        
        return validation_results
    
    def validate_bracket_consistency(self, brackets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate bracket consistency and pairing using stack-based approach."""
        validation_results = {
            "total_brackets": len(brackets),
            "opening_brackets": 0,
            "closing_brackets": 0,
            "valid_pairs": 0,
            "orphaned_openings": [],
            "orphaned_closings": [],
            "bracket_consistency_score": 0.0,
            "bracket_validation_status": "PASSED"
        }
        
        opening_stack = []
        
        for i, bracket in enumerate(brackets):
            if bracket["bracket"] == "<":
                validation_results["opening_brackets"] += 1
                opening_stack.append({
                    "id": bracket["id"],
                    "pos": bracket["pos_in_file"],
                    "index": i
                })
            elif bracket["bracket"] == ">":
                validation_results["closing_brackets"] += 1
                
                if opening_stack:
                    # Valid pair found - pop the matching opening bracket
                    opening = opening_stack.pop()
                    validation_results["valid_pairs"] += 1
                else:
                    # Orphaned closing bracket
                    validation_results["orphaned_closings"].append(bracket["id"])
        
        # Check for orphaned opening brackets
        for opening in opening_stack:
            validation_results["orphaned_openings"].append(opening["id"])
        
        # Calculate bracket consistency score (0.0 to 1.0)
        total_brackets = validation_results["opening_brackets"] + validation_results["closing_brackets"]
        if total_brackets > 0:
            validation_results["bracket_consistency_score"] = (validation_results["valid_pairs"] * 2) / total_brackets
        
        # Determine bracket validation status
        if (len(validation_results["orphaned_openings"]) == 0 and 
            len(validation_results["orphaned_closings"]) == 0 and
            validation_results["bracket_consistency_score"] == 1.0):
            validation_results["bracket_validation_status"] = "PASSED"
        else:
            validation_results["bracket_validation_status"] = "FAILED"
        
        return validation_results
    
    def validate_element_sequence(self, list_tech_tech: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that elements are properly sequenced without gaps or overlaps."""
        validation_results = {
            "total_elements": len(list_tech_tech),
            "validated_pairs": 0,
            "sequence_errors": [],
            "sequence_validation_status": "PASSED",
            "sequence_consistency_score": 0.0
        }
        
        for i in range(len(list_tech_tech) - 1):
            current_elem = list_tech_tech[i]
            next_elem = list_tech_tech[i + 1]
            
            # Check if current element closes exactly before next element opens
            expected_next_open = current_elem["id_close_ttag"] + 1
            actual_next_open = next_elem["id_open_ttag"]
            
            if expected_next_open != actual_next_open:
                error_info = {
                    "pair_index": i,
                    "current_element_id": current_elem["id"],
                    "next_element_id": next_elem["id"],
                    "current_id_close": current_elem["id_close_ttag"],
                    "expected_next_id_open": expected_next_open,
                    "actual_next_id_open": actual_next_open,
                    "gap_or_overlap": actual_next_open - expected_next_open
                }
                validation_results["sequence_errors"].append(error_info)
            else:
                validation_results["validated_pairs"] += 1
        
        # Calculate consistency score
        total_pairs = len(list_tech_tech) - 1
        if total_pairs > 0:
            validation_results["sequence_consistency_score"] = validation_results["validated_pairs"] / total_pairs
        
        # Determine validation status
        if len(validation_results["sequence_errors"]) == 0:
            validation_results["sequence_validation_status"] = "PASSED"
        else:
            validation_results["sequence_validation_status"] = "FAILED"
        
        return validation_results
    
    def perform_cross_validation_analysis(self, validation_details: Dict[str, Any]) -> Dict[str, float]:
        """Perform cross-validation analysis between different validation types."""
        
        comment_val = validation_details["comment_validation"]
        bracket_val = validation_details["bracket_validation"]
        element_val = validation_details["element_sequence_validation"]
        
        # Calculate bracket-comment correlation
        comment_brackets = comment_val.get("total_comment_brackets", 0)
        total_brackets = bracket_val.get("total_brackets", 0)
        bracket_comment_correlation = comment_brackets / total_brackets if total_brackets > 0 else 0.0
        
        # Calculate element-bracket alignment
        element_count = element_val.get("total_elements", 0)
        bracket_pairs = bracket_val.get("valid_pairs", 0)
        element_bracket_alignment = bracket_pairs / element_count if element_count > 0 else 0.0
        
        # Calculate overall structure integrity
        structure_scores = [
            comment_val.get("comment_consistency_score", 0.0),
            bracket_val.get("bracket_consistency_score", 0.0),
            element_val.get("sequence_consistency_score", 0.0)
        ]
        overall_structure_integrity = sum(structure_scores) / len(structure_scores)
        
        return {
            "bracket_comment_correlation": bracket_comment_correlation,
            "element_bracket_alignment": element_bracket_alignment,
            "overall_structure_integrity": overall_structure_integrity
        }
    
    def create_unified_validation_report(self, 
                                       comment_validation: Dict[str, Any],
                                       bracket_validation: Dict[str, Any], 
                                       element_sequence_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Create unified validation report combining all validation types."""
        
        # Collect all validation results
        validation_details = {
            "comment_validation": comment_validation,
            "bracket_validation": bracket_validation,
            "element_sequence_validation": element_sequence_validation
        }
        
        # Calculate overall validation status
        validation_statuses = [
            comment_validation.get("comment_validation_status", "UNKNOWN"),
            bracket_validation.get("bracket_validation_status", "UNKNOWN"),
            element_sequence_validation.get("sequence_validation_status", "UNKNOWN")
        ]
        
        overall_status = "PASSED" if all(status == "PASSED" for status in validation_statuses) else "FAILED"
        
        # Calculate overall validation score
        scores = [
            comment_validation.get("comment_consistency_score", 0.0),
            bracket_validation.get("bracket_consistency_score", 0.0),
            element_sequence_validation.get("sequence_consistency_score", 0.0)
        ]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Generate validation summary
        passed_count = sum(1 for status in validation_statuses if status == "PASSED")
        total_count = len(validation_statuses)
        
        # Cross-validation analysis
        cross_analysis = self.perform_cross_validation_analysis(validation_details)
        
        unified_report = {
            "inputhtmlfilename": self.current_filename if hasattr(self, 'current_filename') else "unknown",
            "validation_timestamp": self.get_current_timestamp(),
            "overall_validation_status": overall_status,
            "overall_validation_score": overall_score,
            "validation_summary": {
                "total_validation_types": total_count,
                "passed_validations": passed_count,
                "failed_validations": total_count - passed_count,
                "validation_coverage": passed_count / total_count if total_count > 0 else 0.0
            },
            "validation_details": validation_details,
            "cross_validation_analysis": cross_analysis
        }
        
        return unified_report
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def run_comprehensive_validation(self, file_path: str) -> Dict[str, Any]:
        """Run all validation types and create unified report."""
        
        # Get brackets and enhanced brackets
        brackets = self.scan_bytes_for_brackets(file_path)
        
        # Read file content for context
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Enhance brackets with context and comment detection
        brackets_with_data = self.enhance_brackets_with_context(brackets, content)
        
        # Mark inner comment content
        brackets_with_data = self.mark_inner_comment_content(brackets_with_data)
        
        # Create tech HTML elements
        list_tech_tech = self.create_tech_tag_html_elements_comms(brackets_with_data, content)
        
        # Run individual validations
        comment_validation = self.validate_comment_consistency(brackets_with_data)
        bracket_validation = self.validate_bracket_consistency(brackets)
        element_sequence_validation = self.validate_element_sequence(list_tech_tech)
        
        # Create unified report
        unified_report = self.create_unified_validation_report(
            comment_validation, bracket_validation, element_sequence_validation
        )
        
        # Save unified validation report
        output_path = self.config.get("output_database_unified_validation", "json/unified_validation.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(unified_report, f, indent=2, ensure_ascii=False)
        
        return unified_report
    
    def run_unified_validation(self):
        """Run unified validation for all input files."""
        print("🔍 Unified Validation System - id_part6 Implementation")
        print("=" * 60)
        
        validation_results = []
        
        for file_path in self.config["input_files"]:
            if not Path(file_path).exists():
                print(f"⚠️ File not found: {file_path}")
                continue
                
            try:
                print(f"📄 Processing file: {file_path}")
                
                # Set current filename for the validation report
                self.current_filename = Path(file_path).name
                
                # Run comprehensive validation
                unified_report = self.run_comprehensive_validation(file_path)
                validation_results.append(unified_report)
                
                # Print validation summary
                overall_status = unified_report.get("overall_validation_status", "UNKNOWN")
                overall_score = unified_report.get("overall_validation_score", 0.0)
                print(f"   ✅ Validation Status: {overall_status}")
                print(f"   📊 Overall Score: {overall_score:.2f}")
                
                # Print detailed results
                validation_summary = unified_report.get("validation_summary", {})
                passed_count = validation_summary.get("passed_validations", 0)
                total_count = validation_summary.get("total_validation_types", 0)
                print(f"   📈 Passed: {passed_count}/{total_count} validation types")
                
                # Print cross-validation analysis
                cross_analysis = unified_report.get("cross_validation_analysis", {})
                if cross_analysis:
                    print(f"   🔗 Cross-Validation Analysis:")
                    print(f"      Bracket-Comment Correlation: {cross_analysis.get('bracket_comment_correlation', 0.0):.2f}")
                    print(f"      Element-Bracket Alignment: {cross_analysis.get('element_bracket_alignment', 0.0):.2f}")
                    print(f"      Overall Structure Integrity: {cross_analysis.get('overall_structure_integrity', 0.0):.2f}")
                
            except Exception as e:
                print(f"❌ Error during unified validation for {file_path}: {e}")
                continue
        
        print(f"\n📊 Unified Validation Summary:")
        print(f"   Processed {len(validation_results)} files")
        
        if validation_results:
            # Calculate overall statistics
            all_passed = all(r.get("overall_validation_status") == "PASSED" for r in validation_results)
            avg_score = sum(r.get("overall_validation_score", 0.0) for r in validation_results) / len(validation_results)
            
            print(f"   Overall Status: {'PASSED' if all_passed else 'FAILED'}")
            print(f"   Average Score: {avg_score:.2f}")
        
        print("✅ Unified validation completed successfully!")
    
    def extract_body_tech_tag_html(self, content: str, pos_open: int, pos_close: int) -> str:
        """Extract body_tech_tag_html content between opening and closing brackets."""
        if pos_open >= pos_close or pos_open < 0 or pos_close > len(content):
            return ""
        
        # Extract content between brackets (excluding the brackets themselves)
        body_content = content[pos_open + 1:pos_close]
        return body_content
    
    def extract_name_tech_tag_html(self, body_content: str) -> str:
        """Extract name_tech_tag_html from body_tech_tag_html content."""
        if not body_content:
            return ""
        
        # Remove leading/trailing whitespace
        body_content = body_content.strip()
        
        # Handle comments
        if body_content.startswith('!--'):
            return "comment"
        
        # Handle DOCTYPE
        if body_content.upper().startswith('!DOCTYPE'):
            return "!doctype"
        
        # Extract first word (tag name)
        parts = body_content.split()
        if parts:
            tag_name = parts[0].lower()
            return tag_name
        
        return ""
    
    def determine_type_ttag(self, name_tech_tag_html: str, body_content: str) -> str:
        """Determine type_ttag based on name_tech_tag_html and body content."""
        if not name_tech_tag_html:
            return "unnamed"
        
        # Get standard tags list from config
        standard_tags = self.config["tech_html_settings"]["standard_tags_list"]
        
        # Check if it's a comment or DOCTYPE
        if name_tech_tag_html in ["comment", "!doctype"]:
            return "unnamed"
        
        # Check if it's a standard HTML tag
        if name_tech_tag_html in standard_tags:
            return "standard_named"
        
        # Check if it's a closing tag (starts with /)
        if name_tech_tag_html.startswith('/'):
            # Extract the actual tag name without /
            actual_name = name_tech_tag_html[1:]
            if actual_name in standard_tags:
                return "standard_named"
            else:
                return "custom"
        
        # If not standard, it's custom
        return "custom"
    
    def create_tech_tag_html_elements(self, brackets: List[Dict[str, Any]], content: str) -> List[Dict[str, Any]]:
        """Create tech_tag_html elements from brackets using TECH_HTML terminology."""
        tech_elements = []
        element_counter = 1
        
        # Group brackets into pairs (opening + closing)
        i = 0
        while i < len(brackets) - 1:
            current_bracket = brackets[i]
            next_bracket = brackets[i + 1]
            
            # Check if we have a valid opening-closing pair
            if (current_bracket["bracket"] == "<" and next_bracket["bracket"] == ">"):
                pos_open_ttag = current_bracket["pos_in_file"]
                pos_close_ttag = next_bracket["pos_in_file"]
                id_open_ttag = current_bracket["id"]
                id_close_ttag = next_bracket["id"]
                
                # Extract body content
                body_tech_tag_html = self.extract_body_tech_tag_html(content, pos_open_ttag, pos_close_ttag)
                
                # Extract name
                name_tech_tag_html = self.extract_name_tech_tag_html(body_tech_tag_html)
                
                # Determine type
                type_ttag = self.determine_type_ttag(name_tech_tag_html, body_tech_tag_html)
                
                # Create element
                element = {
                    "id": element_counter,
                    "id_open_ttag": id_open_ttag,
                    "id_close_ttag": id_close_ttag,
                    "pos_open_ttag": pos_open_ttag,
                    "pos_close_ttag": pos_close_ttag,
                    "type_ttag": type_ttag,
                    "name_tech_tag_html": name_tech_tag_html,
                    "body_tech_tag_html": body_tech_tag_html
                }
                
                tech_elements.append(element)
                element_counter += 1
                
                # Skip the closing bracket in next iteration
                i += 2
            else:
                # Skip single bracket
                i += 1
        
        return tech_elements
    
    def extract_comment_body(self, content: str, pos_open_ttag: int, pos_close_ttag: int) -> str:
        """Extract comment body content between opening and closing positions."""
        # Extract content between comment opening and closing
        # Skip the opening <!-- and closing --> markers
        start_pos = pos_open_ttag + 4  # Skip "<!--"
        end_pos = pos_close_ttag - 3   # Skip "-->"
        
        if start_pos < end_pos:
            comment_body = content[start_pos:end_pos].strip()
            return comment_body
        else:
            return ""
    
    def create_tech_tag_html_elements_comms(self, brackets: List[Dict[str, Any]], content: str) -> List[Dict[str, Any]]:
        """Create comment elements from brackets using TECH_HTML terminology."""
        comment_elements = []
        element_counter = 1
        
        # Stage 1: Process comment elements
        comment_stack = []
        
        for i, bracket in enumerate(brackets):
            if bracket["type_tech_tag"] == "comm_open":
                # Push comment opening to stack
                comment_stack.append({
                    "id": bracket["id"],
                    "pos": bracket["pos_in_file"],
                    "index": i
                })
            elif bracket["type_tech_tag"] == "comm_close":
                if comment_stack:
                    # Found matching comment closing - create comment element
                    opening = comment_stack.pop()
                    pos_open_ttag = opening["pos"]
                    pos_close_ttag = bracket["pos_in_file"]
                    id_open_ttag = opening["id"]
                    id_close_ttag = bracket["id"]
                    
                    # Extract comment body
                    comment_body = self.extract_comment_body(content, pos_open_ttag, pos_close_ttag)
                    
                    # Create comment element
                    comment_element = {
                        "id": element_counter,
                        "id_open_ttag": id_open_ttag,
                        "id_close_ttag": id_close_ttag,
                        "pos_open_ttag": pos_open_ttag,
                        "pos_close_ttag": pos_close_ttag,
                        "type_ttag": "unnamed",
                        "name_tech_tag_html": "comment",
                        "body_tech_tag_html": comment_body
                    }
                    
                    comment_elements.append(comment_element)
                    element_counter += 1
        
        # Stage 2: Process regular HTML elements (skip comment-related brackets)
        regular_brackets = [b for b in brackets if b["type_tech_tag"] == "regular"]
        html_elements = self.create_tech_tag_html_elements(regular_brackets, content)
        
        # Stage 3: Combine and sort all elements by position
        all_elements = comment_elements + html_elements
        
        # Sort elements by pos_open_ttag for consistent chronological order
        all_elements.sort(key=lambda x: x.get("pos_open_ttag", 0))
        
        return all_elements
    
    def process_tech_html_elements(self) -> List[Dict[str, Any]]:
        """Process all files to create TECH_HTML elements."""
        results = []
        
        for file_path in self.config["input_files"]:
            if not Path(file_path).exists():
                print(f"⚠️ File not found: {file_path}")
                continue
                
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Get brackets for this file
                brackets = self.scan_bytes_for_brackets(file_path)
                
                # Enhance brackets with context
                enhanced_brackets = self.enhance_brackets_with_context(brackets, content)
                
                # Create TECH_HTML elements with comment processing
                tech_elements = self.create_tech_tag_html_elements_comms(enhanced_brackets, content)
                
                # Create result
                result = {
                    "inputhtmlfilename": Path(file_path).name,
                    "tech_tag_html_collected": tech_elements,
                    "total_tech_elements": len(tech_elements),
                    "standard_named_elements": len([e for e in tech_elements if e["type_ttag"] == "standard_named"]),
                    "custom_elements": len([e for e in tech_elements if e["type_ttag"] == "custom"]),
                    "unnamed_elements": len([e for e in tech_elements if e["type_ttag"] == "unnamed"])
                }
                results.append(result)
                
            except Exception as e:
                print(f"❌ Error processing TECH_HTML elements for {file_path}: {e}")
                continue
        
        return results
    
    def save_tech_html_results(self, results: List[Dict[str, Any]]):
        """Save TECH_HTML element results to JSON file."""
        output_file = self.config.get("output_database_tech_elements", "json/tech_tag_html_elements.json")
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved TECH_HTML element results to: {output_file}")
    
    def save_bracket_results(self, results: List[Dict[str, Any]]):
        """Save bracket collection results to JSON file."""
        output_file = self.config.get("output_database_byte", "json/all_openclose_bytes.json")
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved bracket results to: {output_file}")
    
    def process_all_files_for_brackets(self) -> List[Dict[str, Any]]:
        """Process all input files for bracket collection."""
        results = []
        
        for file_path in self.config["input_files"]:
            if not Path(file_path).exists():
                print(f"⚠️ File not found: {file_path}")
                continue
                
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Get basic brackets
                brackets = self.scan_bytes_for_brackets(file_path)
                
                # Enhance brackets with context
                enhanced_brackets = self.enhance_brackets_with_context(brackets, content)
                
                result = {
                    "inputhtmlfilename": Path(file_path).name,
                    "brackets_collected": brackets,
                    "brackets_collected_withdata": enhanced_brackets,
                    "total_brackets": len(brackets),
                    "opening_brackets": len([b for b in brackets if b["bracket"] == "<"]),
                    "closing_brackets": len([b for b in brackets if b["bracket"] == ">"])
                }
                results.append(result)
                
            except Exception as e:
                print(f"❌ Error processing brackets for {file_path}: {e}")
                continue
        
        return results
    
    def run_bracket_collection(self):
        """Run the complete bracket collection process."""
        print("🎯 Byte-Level Bracket Collector - TECH_HTML Version")
        print("=" * 50)
        
        print(f"📋 Configuration loaded from: {self.config_file}")
        print(f"📁 Input files: {len(self.config['input_files'])}")
        print(f"💾 Output database: {self.config.get('output_database_byte', 'json/all_openclose_bytes.json')}")
        
        # Collect brackets
        results = self.process_all_files_for_brackets()
        
        # Save results
        self.save_bracket_results(results)
        
        # Print summary
        print("\n📊 Bracket Collection Summary:")
        print(f"   Files processed: {len(results)}")
        
        total_brackets = sum(r.get('total_brackets', 0) for r in results)
        total_opening = sum(r.get('opening_brackets', 0) for r in results)
        total_closing = sum(r.get('closing_brackets', 0) for r in results)
        
        print(f"   Total brackets: {total_brackets}")
        print(f"   Opening brackets (<): {total_opening}")
        print(f"   Closing brackets (>): {total_closing}")
        
        print("✅ Bracket collection completed!")
    
    def run_tech_html_collection(self):
        """Run the complete TECH_HTML element collection process."""
        print("🎯 TECH_HTML Element Collector - Dedicated Version")
        print("=" * 50)
        
        print(f"📋 Configuration loaded from: {self.config_file}")
        print(f"📁 Input files: {len(self.config['input_files'])}")
        print(f"💾 Output database: {self.config.get('output_database_tech_elements', 'json/tech_tag_html_elements.json')}")
        
        # Process TECH_HTML elements
        results = self.process_tech_html_elements()
        
        # Save results
        self.save_tech_html_results(results)
        
        # Print summary
        print("\n📊 TECH_HTML Element Collection Summary:")
        print(f"   Files processed: {len(results)}")
        
        total_elements = 0
        total_standard = 0
        total_custom = 0
        total_unnamed = 0
        
        for result in results:
            total_elements += result.get('total_tech_elements', 0)
            total_standard += result.get('standard_named_elements', 0)
            total_custom += result.get('custom_elements', 0)
            total_unnamed += result.get('unnamed_elements', 0)
        
        print(f"   Total TECH_HTML elements: {total_elements}")
        print(f"   Standard named elements: {total_standard}")
        print(f"   Custom elements: {total_custom}")
        print(f"   Unnamed elements: {total_unnamed}")
        
        print("✅ TECH_HTML element collection completed!")
    
    def run(self):
        """Run the complete TECH_HTML processing pipeline."""
        print("🚀 TECH_HTML Tag Collector - id_part1 Implementation")
        print("=" * 60)
        
        # Load configuration
        print(f"📋 Configuration loaded from: {self.config_file}")
        print(f"📁 Input files: {len(self.config['input_files'])}")
        print(f"💾 Output databases: {self.config.get('output_database_tech_elements', 'json/tech_tag_html_elements.json')}")
        
        # Run bracket collection if enabled
        if self.config.get("enable_bracket_collection", False):
            print("\n" + "=" * 50)
            self.run_bracket_collection()
        
        # Run TECH_HTML element collection if enabled
        if self.config.get("enable_tech_html_collection", False):
            print("\n" + "=" * 50)
            self.run_tech_html_collection()
        
        # Run unified validation if enabled
        if self.config.get("enable_unified_validation", False):
            print("\n" + "=" * 50)
            self.run_unified_validation()
        
        print("\n🎯 TECH_HTML Processing Summary:")
        print("✅ TECH_HTML processing completed successfully!")
        print("📊 Results saved to dedicated TECH_HTML output files")
    
    def loop_tech_html_elements(self):
        """Loop through all TECH_HTML elements in the output database - TECH_HTML version of id_part2."""
        # print("\n🔄 Starting TECH_HTML element loop process - TECH_HTML id_part2")
        # print("=" * 60)
        
        try:
            # Load the TECH_HTML output database
            output_file = self.config.get("output_database_tech_elements", "json/tech_tag_html_elements.json")
            # print(f"📖 Loading TECH_HTML elements from: {output_file}")
            
            with open(output_file, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            if not isinstance(database, list):
                print("❌ Invalid database format - expected list of file results")
                return
            
            total_files = len(database)
            total_elements = 0
            
            # print(f"📁 Found {total_files} files in TECH_HTML database")
            
            # Loop through each file
            for file_index, file_result in enumerate(database, 1):
                input_filename = file_result.get("inputhtmlfilename", f"file_{file_index}")
                tech_elements = file_result.get("tech_tag_html_collected", [])
                
                # print(f"\n📄 File {file_index}/{total_files}: {input_filename}")
                # print(f"   TECH_HTML elements in file: {len(tech_elements)}")

                # Open input file with full path
                input_file_path = f"input/{input_filename}"
                with open(input_file_path, 'r', encoding='utf-8') as f:
                    content_input = f.read()   

                content_test1 = ""
                content_test2 = ""
                content_test3 = ""
                last_split_pos = 0
                ext_new_length = 0
                
                # Sort TECH_HTML elements by order pos_open_ttag 
                sorted_elements = sorted(tech_elements, key=lambda x: x.get("pos_open_ttag", 0))
                
                # Loop through all TECH_HTML elements in this file by order
                for element_index, element in enumerate(sorted_elements, 1):
                    element_id = element.get("id", element_index)
                    pos_open_ttag = element.get("pos_open_ttag", 0)
                    pos_close_ttag = element.get("pos_close_ttag", 0)
                    type_ttag = element.get("type_ttag", "unknown")
                    name_tech_tag_html = element.get("name_tech_tag_html", "unknown")
                    body_tech_tag_html = element.get("body_tech_tag_html", "")

                    # Split content_input by TECH_HTML element positions (id_part6 fix)
                    content_test1 += content_input[last_split_pos:pos_open_ttag]
                    content_test1 += content_input[pos_open_ttag:pos_close_ttag + 1]  # +1 to include >
                    content_test2 += content_input[pos_open_ttag:pos_close_ttag + 1] + "\n"  # +1 to include >
                    content_test3 += content_input[last_split_pos:pos_open_ttag] + "\n"
                    last_split_pos = pos_close_ttag + 1  # +1 to point after the >
                    
                    # print(f"     TECH_HTML Element {element_index} (ID: {element_id}): {name_tech_tag_html}")
                    # print(f"       Position: {pos_open_ttag}-{pos_close_ttag}")
                    # print(f"       Type: {type_ttag}")
                    # print(f"       Body: {body_tech_tag_html[:50]}{'...' if len(body_tech_tag_html) > 50 else ''}")
                    
                    # Special handling for different TECH_HTML element types
                    # if type_ttag == "unnamed":
                    #     print(f"       📝 Unnamed element (comment/DOCTYPE)")
                    # elif type_ttag == "standard_named":
                    #     print(f"       📝 Standard HTML element")
                    # elif type_ttag == "custom":
                    #     print(f"       📝 Custom element")
                    
                    # Process each TECH_HTML element (you can add custom logic here)
                    self.process_single_tech_html_element(element, input_filename, element_index)
                    
                    total_elements += 1
                
                # Save content_test files
                with open(f"output/{input_filename}_tech_test1.html", 'w', encoding='utf-8') as f:
                    f.write(content_test1)
                with open(f"output/{input_filename}_tech_test2.html", 'w', encoding='utf-8') as f:
                    f.write(content_test2)
                with open(f"output/{input_filename}_tech_test3.html", 'w', encoding='utf-8') as f:
                    f.write(content_test3)

                # Length in bytes of content_test1 + ext_new_length by coding utf-8
                length_in_bytes_test1 = len(content_test1.encode('utf-8'))                 
                length_in_bytes_input = len(content_input.encode('utf-8')) + ext_new_length
                
                print(f"   ✅ Length in bytes of content_tech_test1: {length_in_bytes_test1}")                
                print(f"   ✅ Length in bytes of content_input: {length_in_bytes_input}")
                
                print(f"   ✅ Processed {len(tech_elements)} TECH_HTML elements in {input_filename}")
            
            print(f"\n🎯 TECH_HTML Loop Summary:")
            print(f"   Files processed: {total_files}")
            print(f"   Total TECH_HTML elements looped: {total_elements}")
            print("✅ TECH_HTML element loop process completed!")
            
        except FileNotFoundError:
            print(f"❌ TECH_HTML output database not found: {output_file}")
            print("   Run TECH_HTML collection first with: python3 run_tech_tag_collector.py")
        except Exception as e:
            print(f"❌ Error in TECH_HTML element loop process: {e}")
    
    def process_single_tech_html_element(self, element: Dict[str, Any], filename: str, element_index: int):
        """Process a single TECH_HTML element during the loop - customizable logic."""
        # This method can be extended with custom TECH_HTML element processing logic
        # For now, it's a placeholder for future functionality
        
        # Example: You could add TECH_HTML element analysis, validation, or transformation here
        name_tech_tag_html = element.get("name_tech_tag_html", "")
        type_ttag = element.get("type_ttag", "")
        
        # Example processing logic:
        if type_ttag == "standard_named":
            # Process standard HTML elements
            pass
        elif type_ttag == "custom":
            # Process custom elements
            pass
        elif type_ttag == "unnamed":
            # Process comments and DOCTYPE
            pass
        
        # You can add more specific processing logic here
        # For example: TECH_HTML element validation, body content analysis, etc.

def main():
    collector = TechHTMLCollector()
    collector.run()
    
    # Run the TECH_HTML element loop process - TECH_HTML version of id_part2
    collector.loop_tech_html_elements()

if __name__ == "__main__":
    main() 