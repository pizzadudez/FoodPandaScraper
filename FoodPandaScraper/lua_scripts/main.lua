function main(splash)
    ---------------------------------------------------------------------------
    -- JS Helpers
    ---------------------------------------------------------------------------
    local get_coordinates = splash:jsfunc([[
        function() {
            var url = document.querySelector('img.map');
            return url.dataset.imgUrl.match(/\d+.\d+,\d+.\d+/);
        }
    ]])
    local get_topping_id = splash:jsfunc([[
        function(el) {
            return el.dataset.toppingId;
        }
    ]])
    local check_dish_modal_content = splash:jsfunc([[
        function(el) {
            var json = JSON.parse(el.dataset.object);
            var variations = json.product_variations;

            var results = {
                modal: true,
                only_toppings: false,
                click_all_variations: false,
            };
            var topping_id_map = {}

            if (variations.length > 1) {
                results.modal = false;
                for (var i = 0; i < variations.length; i++) {
                    if (variations[i].topping_ids.length) {
                        results.modal = true;
                        break;
                    }
                }

                if (results.modal) {
                    for (var i = 1; i < variations.length; i++) {
                        if (
                            JSON.stringify(variations[i-1].topping_ids) 
                            !== JSON.stringify(variations[i].topping_ids)
                        ) {
                            results.click_all_variations = true;
                            break;
                        }
                    }

                    for (var i = 0; i < variations.length; i++) {
                        var topping_ids = variations[i].topping_ids;
                        for (var j = 0; j < topping_ids.length; j++) {
                            var topping_id = topping_ids[i];
                            topping_id_map[topping_id] = true;
                        }
                    }
                } 
            } else {
                var topping_ids = variations[0].topping_ids;
                if (topping_ids.length) {
                    results.only_toppings = true;
                    for (var i = 0; i < topping_ids.length; i++) {
                        var topping_id = topping_ids[i];
                        topping_id_map[topping_id] = true;
                    }
                } else {
                    results.modal = false;
                }
            }
            results.topping_id_map = topping_id_map;
            return results;
        }
    ]])
    local is_modal_open = splash:jsfunc([[
        function() {
            var display = document.querySelector('#choices-toppings-modal')
            if (!display) return false;
            
            return display.style.display === 'none' ? false : true;
        }
    ]])

    ---------------------------------------------------------------------------
    -- Lua Script
    ---------------------------------------------------------------------------
    splash.private_mode_enabled = false --some elements don't load in private mode
    assert(splash:go(splash.args.url))
    splash:wait(1.95)
    splash:set_viewport_full()
    
    -- Submit Address (needed to click on dishes with modals)
    local address_input = assert(splash:select('.restaurants-search-form__input'))
    local address_verify_button = assert(splash:select('.restaurants-search-form__button--full'))
    local coords = get_coordinates()
    address_input:mouse_click{}
    splash:send_text(coords)
    address_verify_button:mouse_click{}
    splash:wait(1.95)
    
    -- Response Table
    local response = {}
    response.html = splash:html()
    response.topping_selectors = {}
    local topping_selectors = response.topping_selectors

    -- Extract topping selector outerHTML
    local function add_topping_selectors(modal)
        local toppings = modal:querySelectorAll('div.topping')
        for _, topping in ipairs(toppings) do
            local topping_container = topping:querySelector('div.product-topping-list')
            local topping_id = get_topping_id(topping_container)
            topping_selectors[topping_id] = topping_selectors[topping_id] or topping.node.outerHTML
        end
    end
    -- Topping Selectors can be shared by multiple dishes
    local function has_new_toppings(map)
        for topping_id, _ in pairs(map) do
            if not topping_selectors[topping_id] then return true end;
        end
        return false;
    end

    -- Loop over all dishes modals (topping selectors)
    local dishes = splash:select_all('div.dish-card.menu__item')
    for _, dish in ipairs(dishes) do
        local results = check_dish_modal_content(dish)
        -- Only parse if topping_ids are new
        if results.modal and has_new_toppings(results.topping_id_map) then
            -- Open Modal
            dish:click{}
            while not is_modal_open() do splash:wait(math.random(0.2, 0.25)) end
            splash:wait(math.random(2.2, 2.4))
            local modal = splash:select('#choices-toppings-modal .modal-body')
            -- Add Topping Selectors if present
            if not results.only_toppings then
                -- variation elements get replaced after every variation selection
                local variations = modal:querySelectorAll('div.product-topping-item')
                for variation_num, _ in ipairs(variations) do
                    local variation = modal:querySelectorAll(
                        'div.product-topping-item .radio-box.variation')[variation_num]
                    variation:click{}
                    splash:wait(math.random(1.5, 1.7))
                    add_topping_selectors(modal)
                    -- If all variations have the same toppings stop here
                    if not results.click_all_variations then break end
                end
            elseif results.only_toppings then
                add_topping_selectors(modal)
            end
            -- Close Modal
            splash:send_keys('<Escape>')
            while is_modal_open() do splash:wait(math.random(0.2, 0.25)) end
            splash:wait(math.random(1, 1.2))
        end
    end

    return response
end