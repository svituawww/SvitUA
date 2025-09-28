            SELECT
            f1.file_path, 
            f1.dir_or_file,
            CASE 
            WHEN f1.end_fp = f1.beg_fp THEN 'Replace'
            WHEN f1.end_fp = 'Delete' THEN 'Delete'
            WHEN f1.beg_fp = 'New' THEN 'New'
            ELSE 'Unknown'
            END as file_action
            from
            (
            SELECT
            count(o1.file_path) as count_ids, o1.file_path as file_path, o1.dir_or_file as dir_or_file, coalesce(se.file_path,'Delete') as end_fp , coalesce(sb.file_path,'New') as beg_fp
            from
            (
            SELECT
            count(ids) as count_ids, file_path, file_name, file_hash, dir_or_file
            from
            (
            SELECT
            1 as ids, sf.file_path, sf.file_name, sf.file_hash, sf.dir_or_file
            FROM
            snapshots_files sf
            WHERE
            sf.id_snapshot_ref = 1

            union ALL

            SELECT
            2 as ids, sf.file_path, sf.file_name, sf.file_hash, sf.dir_or_file
            FROM
            snapshots_files sf
            WHERE
            sf.id_snapshot_ref = (select max(id) from snapshot_ref)

            )
            group by 2,3,4
            )o1

            left join (
            SELECT
            sf.file_path, sf.file_hash, sf.id_snapshot_ref
            FROM
            snapshots_files sf
            WHERE
            sf.id_snapshot_ref = (select max(id) from snapshot_ref)

            )se on se.file_path = o1.file_path

            left join (
            SELECT
            sf.file_path, sf.file_name, sf.file_hash, sf.id_snapshot_ref
            FROM
            snapshots_files sf
            WHERE
            sf.id_snapshot_ref = 1

            )sb on sb.file_path = o1.file_path

            where
            o1.count_ids <> 2
            group by 2,3,4,5
            )f1
