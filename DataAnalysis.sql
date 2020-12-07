use Databaste;

-- 25 most common molecules in the top 100 rated recipes
select pubchem_id, 
	molecule_name, 
    count(*) as 'count' 
from recipe
join amount using (recipe_id)
join ingredient  using(ingredient_id)
join composition using (ingredient_id)
join molecule using (pubchem_id)
where recipe_id in 
	(select * from
		(select recipe_id from recipe
		join review using (recipe_id)
		group by recipe_id
		order by avg(rating)
		limit 100) tmp)
group by pubchem_id, molecule_name
order by count desc
limit 25;


-- 25 most common flavors in the top 100 rated recipes
select flavor_name, 
	count(flavor_name) as 'count' 
from recipe
join amount using (recipe_id)
join ingredient using (ingredient_id)
join composition using (ingredient_id)
join property using (pubchem_id)
join flavor using (flavor_id)
where recipe_id in 
	(select * from
		(select recipe_id from recipe
		join review using (recipe_id)
		group by recipe_id
		order by avg(rating)
		limit 100) tmp)
group by flavor_id, flavor_name
order by count desc
limit 25;

