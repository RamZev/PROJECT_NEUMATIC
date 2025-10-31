# neumatic\apps\menu\context_processors.py
from .models import MenuHeading, MenuItem

def menu_context(request):
    if not request.user.is_authenticated:
        return {}
    
    headings = MenuHeading.objects.all().order_by('order')
    menu_tree = {}
    
    for heading in headings:
        items = MenuItem.objects.filter(heading=heading, parent=None).order_by('order')
        visible_items = []
        
        for item in items:
            # Cargar recursivamente todos los niveles hijos
            children_tree = build_menu_tree(item)
            if item.is_collapse and not children_tree:
                continue
            visible_items.append({
                'item': item, 
                'children': children_tree
            })
        
        if visible_items:
            menu_tree[heading] = visible_items
    
    return {'menu_tree': menu_tree}

def build_menu_tree(menu_item):
    """
    Función recursiva para construir el árbol completo del menú
    """
    children = MenuItem.objects.filter(parent=menu_item).order_by('order')
    children_tree = []
    
    for child in children:
        grandchildren = build_menu_tree(child)
        
        children_tree.append({
            'item': child,
            'children': grandchildren
        })
    
    return children_tree