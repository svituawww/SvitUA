#!/usr/bin/env python3
"""
Simple HTML Reconstructor
Tests reconstruction from parsed elements
"""

import json
from pathlib import Path
from typing import List, Dict, Any

class SimpleReconstructor:
    def __init__(self):
        pass
    
    def reconstruct_from_elements(self, elements: List[Dict[str, Any]]) -> str:
        """Reconstruct HTML from parsed elements."""
        # Sort elements by start_pos to maintain order
        sorted_elements = sorted(elements, key=lambda x: x.get('start_pos', 0))
        
        reconstructed = ""
        for element in sorted_elements:
            if element['name'] == 'text':
                reconstructed += element['inner_content']
            elif element['name'] == 'comment':
                reconstructed += element['inner_content']
            elif element['name'] == 'doctype':
                reconstructed += element['element_attr_content']
            elif element['name'] == 'tag':
                reconstructed += element['element_attr_content']
        
        return reconstructed
    
    def save_reconstructed(self, content: str, output_file: Path):
        """Save reconstructed HTML."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 Saved reconstructed HTML to: {output_file}")

def main():
    # Test FSM parser results
    fsm_json = Path("svituawww.github.io/output/fsm_elements_parsed.json")
    fsm_output = Path("svituawww.github.io/output/fsm_reconstructed.html")
    
    # Test Binary parser results
    binary_json = Path("svituawww.github.io/output/binary_elements_parsed.json")
    binary_output = Path("svituawww.github.io/output/binary_reconstructed.html")
    
    original_file = Path("svituawww.github.io/output/index_html_.html")
    
    reconstructor = SimpleReconstructor()
    
    # Test FSM reconstruction
    if fsm_json.exists():
        print("🔍 Testing FSM reconstruction...")
        with open(fsm_json, 'r', encoding='utf-8') as f:
            fsm_elements = json.load(f)
        
        fsm_reconstructed = reconstructor.reconstruct_from_elements(fsm_elements)
        reconstructor.save_reconstructed(fsm_reconstructed, fsm_output)
        
        # Compare with original
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        fsm_match = fsm_reconstructed == original_content
        print(f"FSM Reconstruction: {'✅ MATCH' if fsm_match else '❌ DIFFERENT'}")
        print(f"FSM Length: {len(fsm_reconstructed)} vs Original: {len(original_content)}")
    
    # Test Binary reconstruction
    if binary_json.exists():
        print("\n🔍 Testing Binary reconstruction...")
        with open(binary_json, 'r', encoding='utf-8') as f:
            binary_elements = json.load(f)
        
        binary_reconstructed = reconstructor.reconstruct_from_elements(binary_elements)
        reconstructor.save_reconstructed(binary_reconstructed, binary_output)
        
        # Compare with original
        binary_match = binary_reconstructed == original_content
        print(f"Binary Reconstruction: {'✅ MATCH' if binary_match else '❌ DIFFERENT'}")
        print(f"Binary Length: {len(binary_reconstructed)} vs Original: {len(original_content)}")
    
    # Test Perfect parser results
    perfect_json = Path("svituawww.github.io/output/perfect_elements_parsed.json")
    perfect_output = Path("svituawww.github.io/output/perfect_reconstructed.html")
    
    if perfect_json.exists():
        print("\n🔍 Testing Perfect reconstruction...")
        with open(perfect_json, 'r', encoding='utf-8') as f:
            perfect_elements = json.load(f)
        
        perfect_reconstructed = reconstructor.reconstruct_from_elements(perfect_elements)
        reconstructor.save_reconstructed(perfect_reconstructed, perfect_output)
        
        # Compare with original
        perfect_match = perfect_reconstructed == original_content
        print(f"Perfect Reconstruction: {'✅ MATCH' if perfect_match else '❌ DIFFERENT'}")
        print(f"Perfect Length: {len(perfect_reconstructed)} vs Original: {len(original_content)}")

if __name__ == "__main__":
    main() 