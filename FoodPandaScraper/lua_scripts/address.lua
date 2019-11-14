function main(splash)
    ---------------------------------------------------------------------------
    -- JS Helpers
    ---------------------------------------------------------------------------
    local get_coordinates_old = splash:jsfunc([[
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
                            var topping_id = topping_ids[j];
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
            var modal = document.querySelector('#choices-toppings-modal');
            if (!modal) return false;
            
            return modal.style.display === 'block' ? true : false;
        }
    ]])
    local is_map_modal_open = splash:jsfunc([[
        function() {
            var map = document.querySelector('div.modal.map-modal');
            if (!map) return false;
            return map.style.display === 'block' ? true : false;
        }
    ]])
    local is_address_verified = splash:jsfunc([[
        function() {
            var address_bar = document.querySelector('div.menu__postal-code-bar');
            return address_bar.classList.contains('hide')
        }
    ]])
    local get_coordinates = splash:jsfunc([[
        function() {
            var el = document.querySelector('div.menu__list-wrapper')
            var data = JSON.parse(el.dataset.vendor)
            return {
                latitude: data.latitude,
                longitude: data.longitude
            }
        }
    ]])
    local input_coords = splash:jsfunc([[
        function(lat, long) {
            var input = document.querySelector('input.restaurants-search-form__input')
            input.value = lat + ' ' + long;
            var submit = document.querySelector('button.restaurants-search-form__button--full');
            submit.click()
        }
    ]])

    ---------------------------------------------------------------------------
    -- Lua Script
    ---------------------------------------------------------------------------
    local treat = require("treat")
    splash.private_mode_enabled = false --some elements don't load in private mode
    assert(splash:go(splash.args.url))
    --splash:set_viewport_full()
    splash:wait(4.95)
    
    -- Response Table
    local response = {}
    response.debug = {}
    treat.as_array(response.debug)
    response.topping_selectors = {}
    local topping_selectors = response.topping_selectors
    response.html = splash:html()


    -- Debugging with screenshots
    local function debug(text, png)
        table.insert(response.debug, {text = text, content = png})
    end
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
    -- Modal wait timeout
    local function modal_open_timeout()
        local tries = 20
        while tries > 0 and not is_modal_open() do
            splash:wait(math.random(0.2, 0.25))
            tries = tries - 1
        end
    end


    -- Submit Address (needed to click on dishes with modals)
    local coords = get_coordinates()
    input_coords(coords.latitude, coords.longitude)
    splash:wait(2)
    -- Coords can fail (rarely), submit slightly altered coords
    if is_map_modal_open() then
        local x_axis = false
        local positive = 1
        local change_axis = true
        local value = 0.005
        local tries = 0
        while not is_address_verified() do
            local lat, long = coords.latitude, coords.longitude
            if x_axis then 
                lat = lat + (positive * value)
            else 
                long = long + (positive * value)
            end

            input_coords(lat, long)
            splash:wait(math.random(1.7, 1.9))
            tries = tries + 1
        debug('try#: '..tries..' '..lat..' '..long, splash:png())
            if tries > 9 then break end

            -- change values for next iterration
            if tries % 4 == 0 then value = value + value end
            if change_axis then
                x_axis = not x_axis
            else
                positive = positive * -1
            end
            change_axis = not change_axis
        end
    end
    -- Give up and return html only
    if not is_address_verified() then
        return response
    end
    
    -- Loop over all dishes modals (topping selectors)
    local dishes = splash:select_all('div.dish-card.menu__item')
    for _, dish in ipairs(dishes) do
        local results = check_dish_modal_content(dish)
        -- Only parse if topping_ids are new
        if results.modal and has_new_toppings(results.topping_id_map) then
            -- Open Modal
            dish:click{}
            modal_open_timeout()
            splash:wait(math.random(1.2, 1.4))
            if not is_modal_open() then
                debug('Toppings Modal could not be opened', nil)
                return response 
            end

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