(function(){

if(Splunk.util.getCurrentView() == "sdiff-adv") {
        // TODO: Purge memory of below from brain
        $(document).ready(function() {

            if (Splunk.Module.PostProcessFilter) {
                Splunk.Module.PostProcessFilter = $.klass(Splunk.Module.PostProcessFilter, {
                    /**
                     * Handles refresh of sdiffhtml
                     */
                    onContextChange: function(){
                        alert("hello world");
                    }
                });
            }
        });
}
})();
