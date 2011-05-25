store.js
--------
    // public interface
    meta_data ( value )
    meta_datasets ()
    meta_perspectives ( dataset_id )    
    create_new_group ( id )
    dataset ()
    perspective ()
    issue ()    
    active_columns ()
    active_rows ()    
    active_pending_nodes ()
    
    // private interface
    active_group ( value )
    active_sheet ( value )
    find_group ( id )
    new_sheet ( c, r, n )
    new_group ( id )


db.js
-----    
    // public interface
    get_init_data ()
    download_node ( parent_id )
    add_pending_node ( id )
    remove_pending_node ( id )


