use Databaste;

-- Get the 15 molecules with the highest average rating
select pubchem_id, 
	molecule_name,
    avg(rating) as 'avg' 
from molecule
join composition using (pubchem_id)
join amount using (ingredient_id)
join recipe using (recipe_id)
join review using (recipe_id)
group by pubchem_id
order by avg desc
limit 15;


-- Get the flavors for the top 2 rated molecules
select flavor_name, 
	count(flavor_name) as 'count' 
from molecule 
join property using (pubchem_id)
join flavor using (flavor_id)
where pubchem_id in (select * from 
	(select pubchem_id from molecule
	join composition using (pubchem_id)
	join amount using (ingredient_id)
	join recipe using (recipe_id)
	join review using (recipe_id)
	group by pubchem_id
	order by avg(rating) desc
	limit 2)tmp)
group by flavor_name
order by count desc, flavor_name; 
