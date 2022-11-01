require("oltp_common")

function prepare_statements()
    /*delete*/
   prepare_for_each_table("deletes")

   /*read write*/
    if not sysbench.opt.skip_trx then
      prepare_begin()
      prepare_commit()
   end

   prepare_point_selects()

   if sysbench.opt.range_selects then
      prepare_simple_ranges()
      prepare_sum_ranges()
      prepare_order_ranges()
      prepare_distinct_ranges()
   end

   prepare_index_updates()
   prepare_non_index_updates()
   prepare_delete_inserts()
end


function delete(){
  local tnum = sysbench.rand.uniform(1, sysbench.opt.tables)
   local id = sysbench.rand.default(1, sysbench.opt.table_size)

   param[tnum].deletes[1]:set(id)
   stmt[tnum].deletes:execute()
}


function event()
 
    delete()

    if not sysbench.opt.skip_trx then
      begin()
   end

   execute_point_selects()

   if sysbench.opt.range_selects then
      execute_simple_ranges()
      execute_sum_ranges()
      execute_order_ranges()
      execute_distinct_ranges()
   end

   execute_index_updates()
   execute_non_index_updates()
   execute_delete_inserts()

   if not sysbench.opt.skip_trx then
      commit()
   end

   check_reconnect()


end
