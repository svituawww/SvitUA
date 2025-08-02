
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
```




SELECT pos_open_ttag, pos_close_ttag, file_id, type_ttag, name_tech_tag_html  FROM tech_html_elements  LIMIT 5;

lets create loop by each reacord and element in sql query and print it


<!-- PRESERVE end id_part1 -->




