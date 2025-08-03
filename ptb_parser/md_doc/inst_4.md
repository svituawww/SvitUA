<!-- File Processing → Brackets → Elements → Validation → Content Extraction → Summary -->


<!-- PRESERVE begin id_part1 -->

create this table

CREATE TABLE content_tech_html (
    content_id INTEGER,           -- Auto-incremental per file_id
    techhtml_id_start INTEGER,          
    techhtml_id_end INTEGER,
    file_id INTEGER NOT NULL,
    pos_start INTEGER NOT NULL,
    pos_end INTEGER NOT NULL,
    content_body TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (file_id, content_id),  -- Composite primary key
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (techhtml_id_start) REFERENCES tech_html_elements(techhtml_id),
    FOREIGN KEY (techhtml_id_end) REFERENCES tech_html_elements(techhtml_id)    
);



SELECT pos_open_ttag, pos_close_ttag, file_id, type_ttag, name_tech_tag_html  FROM tech_html_elements  LIMIT 5;

lets create loop by each reacord and element in sql query and print it


<!-- PRESERVE end id_part1 -->


<!-- PRESERVE begin id_part2 -->


lets move this function to another module: extract_content_items.py and include it to ptb_parser/scripts/enhanced_tech_html_parser.py

    def extract_href_from_element(self, content_body: str) -> str:
        """Extract href from an element."""
        # use regex to extract href from content_body
        href_pattern = r'href="([^"]+)"'
        match = re.search(href_pattern, content_body)
        if match:
            return match.group(1)
        return None

    def extract_src_from_element(self, content_body: str) -> str:
        """Extract src from an element."""
        # use regex to extract src from content_body
        src_pattern = r'src="([^"]+)"'
        match = re.search(src_pattern, content_body)
        if match:
            return match.group(1)
        return None

    def extract_alt_from_element(self, content_body: str) -> str:
        """Extract alt from an element."""
        # use regex to extract alt from content_body
        alt_pattern = r'alt="([^"]+)"'
        match = re.search(alt_pattern, content_body)
        if match:
            return match.group(1)
        return None

    def extract_rel_from_element(self, content_body: str) -> str:
        """Extract rel from an element."""
        # use regex to extract rel from content_body
        rel_pattern = r'rel="([^"]+)"'
        match = re.search(rel_pattern, content_body)
        if match:
            return match.group(1)
        return None



<!-- PRESERVE end id_part2 -->
