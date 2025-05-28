def test_jadeship_conversion():
    """Test link conversion with agent priority"""
    from src.processors.link_converter import JadeshipConverter
    converter = JadeshipConverter()
    result = converter.convert_link('https://item.taobao.com/item.htm?id=123456789')
    assert result['agent_used'] == 'allchinabuy'  # Should use primary agent
    assert result['success'] is True
