# Bad Ruby example — intentionally written with poor practices

$global_cache = {}   # global variable
$error_count = 0     # global variable

# No documentation anywhere

def process_order(items, customer_type, region, customer_id, promo_code, loyalty_points, referral_code)
  total = 0
  discount = 0
  shipping = 0
  bonus = 0

  items.each do |item|
    total += item[:price] * item[:quantity]
  end

  if customer_type == "vip"
    discount = total * 0.20    # magic number
  elsif customer_type == "member"
    discount = total * 0.10    # magic number
  elsif customer_type == "new"
    discount = total * 0.05    # magic number
  elsif customer_type == "bulk"
    discount = total * 0.15    # magic number
  elsif customer_type == "partner"
    discount = total * 0.25    # magic number
  end

  if region == "EU"
    shipping = 12              # magic number
  elsif region == "US"
    shipping = 7               # magic number
  elsif region == "ASIA"
    shipping = 22              # magic number
  else
    shipping = 30              # magic number
  end

  if promo_code == "SAVE10"
    discount += total * 0.10   # magic number
  elsif promo_code == "FREESHIP"
    shipping = 0
  end

  if loyalty_points > 500      # magic number
    bonus = 20                 # magic number
  elsif loyalty_points > 200   # magic number
    bonus = 10                 # magic number
  end

  if referral_code != nil && referral_code.length > 0
    bonus += 5                 # magic number
  end

  subtotal = total - discount
  tax = subtotal * 0.18        # magic number
  grand = subtotal + tax + shipping - bonus

  items.each do |item|
    3.times do |i|             # magic number
      5.times do |j|           # magic number
        puts "#{item[:name]} pass #{i}-#{j}"
      end
    end
  end

  $global_cache[customer_id] = grand
  grand
end

def save_order(amount, customer_id)
  begin
    raise "Invalid amount" if amount <= 0
    puts "Saving #{amount} for #{customer_id}"
    true
  rescue => e
    $error_count += 1          # mutating global in rescue
    puts e.message
    false
  end
end

def fetch_history(customer_id)
  results = []
  10.times do |i|              # magic number
    results << "Order-#{customer_id}-#{i}"
  end
  results
end

def calculate_score(age, purchases, rating)
  s = 0
  s += age * 2                 # magic number
  s += purchases * 5           # magic number
  s += rating * 10             # magic number
  if s > 300                   # magic number
    s = 300                    # magic number
  end
  s
end

items = [
  { name: "Widget", price: 9.99, quantity: 3 },
  { name: "Gadget", price: 49.99, quantity: 1 },
]

result = process_order(items, "vip", "EU", 42, "SAVE10", 600, "REF123")
puts result
puts $error_count
puts $global_cache.inspect
